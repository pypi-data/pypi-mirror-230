import argparse
import json
import os.path
import shutil
import subprocess
import time
from urllib import parse

from metaloop.client.mds import MDS
from metaloop.exception import InvalidParamsError
from metaloop.utils.zip import unzip_file


def parse_args():
    parser = argparse.ArgumentParser(description='export and download data from metaloop')
    parser.add_argument('--api_addr', required=True, help='address of metaloop API')
    parser.add_argument('--user_token', required=True, help='user token used to access metaloop API')
    parser.add_argument('--import_file_path', default='', help='import train repo path')
    parser.add_argument('--password', default='', help='zip uncompressed password')
    return parser.parse_args()


def metaloop_dir_exist_and_move_json(parent_path):
    if 'metaloop_data' not in os.listdir(parent_path):
        raise ValueError(f"{parent_path} not a metaloop directory, not valid dataset file")
    move_path = os.path.join(parent_path, "metaloop_data")
    move_path_list = os.listdir(move_path)
    if len(move_path_list) == 1 and os.path.isdir(os.path.join(move_path, move_path_list[0])):
        move_path = os.path.join(move_path, move_path_list[0])
    shutil.copy(os.path.join(parent_path, "output.json"), os.path.join(move_path, "output.json"))
    return move_path


class TrainRepoImport:
    def __init__(
            self,
            user_token: str,
            api_addr: str,
            import_file_path: str,
            password: str
    ) -> None:
        self.repo_id_dataset_ids = {}
        self.user_token = user_token
        self.api_addr = api_addr
        self.password = password
        self.repo_json = {}
        self.mds_client = MDS(user_token, api_addr)
        if not os.path.exists(import_file_path):
            raise InvalidParamsError(f"{import_file_path} not exists")
        self.import_file_path = import_file_path
        self.import_path = ""
        self.unzip_path = ""

    def upload_s3_file(self):
        s3_path = os.path.join(self.import_path, "s3_path")
        if os.path.exists(s3_path):
            for bucket in os.listdir(s3_path):
                bucket_path = os.path.join(s3_path, bucket)
                for dir in os.listdir(bucket_path):
                    self.mds_client.upload_files_to_s3_storage(bucket, os.path.join(bucket_path, dir))

    def create_version_and_get(self, ds_name_version):
        index = ds_name_version.rindex("V")
        if index == -1:
            raise ValueError(f"{ds_name_version} not a valid dataset name")
        ds_name = ds_name_version[:index - 1]
        if self.mds_client.exist_dataset(ds_name):
            dataset = self.mds_client.get_dataset(ds_name)
            dataset.create_version(comment="train repo import")
        else:
            dataset = self.mds_client.create_dataset(
                ds_name,
                "image",
                [],
                comment="repo import"
            )
        dataset.summary()
        return dataset

    def upload_repo_dataset(self, dataset_path, repo):
        repo_path = os.path.join(dataset_path, repo)
        if "dataset_relation" not in self.repo_json[repo]:
            raise ValueError(f"{ self.repo_json[repo]} not dataset_relation")
        dataset_relation = self.repo_json[repo]["dataset_relation"]
        test_dataset_ids = []
        train_dataset_ids = []
        model_test_dataset_ids = []
        for ds_name_version in os.listdir(repo_path):
            dataset = self.create_version_and_get(ds_name_version)
            dr_nv = dataset_relation[ds_name_version]
            if "test" in dr_nv:
                test_dataset_ids.append(dataset.id)
            if "train" in dr_nv:
                train_dataset_ids.append(dataset.id)
            if "model_test" in dr_nv:
                model_test_dataset_ids.append(dataset.id)
            ds_path = os.path.join(dataset_path, repo, ds_name_version)
            ds_path = os.path.join(ds_path, "metaloop")
            # move_path = metaloop_dir_exist_and_move_json(ds_path)
            dataset.import_data(ds_path, "pre_annotation")

        self.repo_id_dataset_ids[repo] = {
            "test_dataset_ids": test_dataset_ids,
            "train_dataset_ids": train_dataset_ids,
            "model_test_dataset_ids": model_test_dataset_ids
        }

    def upload_dataset(self):
        dataset_path = os.path.join(self.import_path, "dataset_path")
        if not os.path.exists(dataset_path):
            return None

        for repo in os.listdir(dataset_path):
            self.upload_repo_dataset(dataset_path, repo)

    def load_docker_image(self):
        image = os.path.join(self.import_path, "image.tar")
        if os.path.exists(image):
            print("load docker image")
            load_args = ['docker', 'load', '-i', image]
            # 调用 Docker 命令保存多个镜像为 tar 文件
            proc = subprocess.Popen(load_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            # 输出保存日志
            if proc.returncode == 0:
                print('docker load images {} successfully.'.format(image))
            else:
                print('docker load images failed. Error message:\n', err.decode('utf-8'))
                raise Exception(err.decode('utf-8'))

    def upload_train_repo(self):
        for str_id, repo in self.repo_json.items():
            repo_name = repo["name"]
            post_data = {
                "name": repo_name,
                "accuracy": True,
                "limit": 10000,
            }
            resp_train_repos = self.mds_client.search_train_task_template(post_data)
            skip = False
            if len(resp_train_repos) > 0:
                for ver in resp_train_repos[0]["versions"]:
                    if ver["version"] == repo["version"]:
                        skip = True
                        print(f"{repo_name} train template already exists, skipped")
                        break
            if skip:
                continue

            if str_id in self.repo_id_dataset_ids:
                dataset_ids = self.repo_id_dataset_ids[str_id]
                if "test_dataset_ids" in dataset_ids:
                    repo["test_dataset_ids"] = dataset_ids["test_dataset_ids"]
                if "train_dataset_ids" in dataset_ids:
                    repo["train_dataset_ids"] = dataset_ids["train_dataset_ids"]
                model_test_ids = dataset_ids.get("model_test_dataset_ids", [])
                if len(model_test_ids) > 0:
                    if "model_config" in repo:
                        model_config_str = repo["model_config"]
                        model_config = json.loads(model_config_str)
                        if "default" in model_config:
                            plant_id = str(model_config["default"])
                            plant = model_config[plant_id]
                            if "abaddonlist" in plant:
                                plant["abaddonlist"] = model_test_ids[0]
                                plant["secondSelect"] = model_test_ids[0]
                                model_config_str = json.dumps(model_config, ensure_ascii=False)
                                repo["model_config"] = model_config_str

            self.mds_client.create_train_task_template(repo)

    def unzip_repo(self):
        unzip_path = f"/tmp/import_repo/{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        # unzip_path = "/tmp/import_repo/20230506192027"
        self.unzip_path = unzip_path
        unzip_file(self.import_file_path, self.password, unzip_path)
        path_dirs = os.listdir(unzip_path)
        import_path = unzip_path
        while len(path_dirs) == 1:
            d = path_dirs[0]
            import_path = os.path.join(import_path, d)
            path_dirs = os.listdir(import_path)

        self.import_path = import_path
        repo_json_path = os.path.join(import_path, "repo.json")
        if not os.path.exists(repo_json_path):
            raise InvalidParamsError("zip invalid not repo info")
        with open(repo_json_path, 'r') as f:
            self.repo_json = json.load(f)

    def import_pipeline_template(self):
        repo_json_path = os.path.join(self.import_path, "pipe.json")
        if os.path.exists(repo_json_path):
            with open(repo_json_path, 'r') as f:
                pipe_json = json.load(f)
            for pipe in pipe_json:
                if len(self.mds_client.get_pipe_template_by_id(pipe["pipeline_template_id"])) == 0:
                    pipe["import"] = True
                    self.mds_client.create_pipe_template(pipe)
                else:
                    print(f"pipeline_template id {pipe['pipeline_template_id']} already exists skipped")

    def upload(self):
        print("repo importing")
        self.unzip_repo()
        self.load_docker_image()
        self.upload_s3_file()
        self.upload_dataset()
        self.upload_train_repo()
        self.import_pipeline_template()
        shutil.rmtree(self.unzip_path)


if __name__ == '__main__':
    args = parse_args()
    TrainRepoImport(args.user_token, args.api_addr, args.import_file_path, args.password).upload()
