import argparse
import json
import os.path
import shutil
import subprocess
import time
from urllib import parse
from urllib.request import urlretrieve

from metaloop.client.mds import MDS
from metaloop.exception import InvalidParamsError
from metaloop.utils.zip import unzip_file, zip_files_with_password


def parse_args():
    parser = argparse.ArgumentParser(description='export and download data from metaloop')
    parser.add_argument('--api_addr', required=True, help='address of metaloop API')
    parser.add_argument('--user_token', required=True, help='user token used to access metaloop API')
    parser.add_argument('--train_repo_ids', required=True, help='IDs of train repo to export')
    parser.add_argument('--pipe_template_ids', required=False, default="", help='IDs of pipe template to export')
    parser.add_argument('--pack_image', required=False, default=False, help='whether to package the image')
    parser.add_argument('--export_file_name', required=True, default='', help='export data file name')
    parser.add_argument('--password', required=True, default='', help='zip compressed password')
    return parser.parse_args()


# 定义Shell脚本内容
docker_script = """
#!/bin/bash

# 检查镜像是否存在
if [ 1 -eq `docker images -q "$0" | wc -l` ] ; then
    echo "Docker image "$0" exists."
else
    echo "Docker image "$0" does not exist, pulling..."
    docker pull "$0"
fi
"""


def pull_docker_images_if_not_present(image):
    # 执行Shell脚本
    process = subprocess.Popen(
        [docker_script, image],
        shell=True,
        stderr=subprocess.PIPE
    )
    _, err_msg = process.communicate()
    # 输出保存日志
    if process.returncode == 0:
        print('Docker images pull to {} successfully.'.format(image))
    else:
        raise Exception('Docker save failed. Error message:\n', err_msg.decode('utf-8'))


class TrainRepoExport:
    def __init__(
            self,
            user_token: str,
            api_addr: str,
            export_file_name: str,
            train_repo_ids: str,
            pipe_template_ids: str,
            pack_image: str,
            password: bool,
    ) -> None:
        self.user_token = user_token
        self.api_addr = api_addr
        self.password = password
        self.train_repo_ids = train_repo_ids.split(',')
        if len(self.train_repo_ids) == 0:
            raise InvalidParamsError("train_repo_ids not empty")

        if pipe_template_ids != '':
            self.pipe_template_ids = pipe_template_ids.split(',')
        else:
            self.pipe_template_ids = []

        if os.path.exists(export_file_name):
            raise InvalidParamsError(f"{export_file_name} exists")
        self.file_name = export_file_name

        if pack_image.lower() == 'true':
            self.pack_image = True
        else:
            self.pack_image = False
        self.image = []
        self.repo_json = {}
        date_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.output_path = f"/tmp/export_repo/{date_time}"
        os.makedirs(self.output_path)
        self.mds_client = MDS(self.user_token, self.api_addr)

    def export_pipeline_template(self):
        pipe_json = []
        if len(self.pipe_template_ids) > 0:
            for pipe_id in self.pipe_template_ids:
                pipe = self.mds_client.get_pipe_template_by_id(pipe_id, True)
                if len(pipe) == 0:
                    raise InvalidParamsError(f"pipe template {pipe_id} not found")
                pipe = pipe[0]
                if "image" in pipe and isinstance(pipe["image"], list):
                    self.image.extend(pipe["image"])
                if "s3_url" in pipe and isinstance(pipe["s3_url"], list):
                    s3_path = os.path.join(self.output_path, "s3_path")
                    for url in pipe["s3_url"]:
                        if url.startswith("/"):
                            url = url[1:]
                        index = url.index('/')
                        bucket = url[:index]
                        path = url[index + 1:]
                        self.mds_client.download_files_from_s3_storage(bucket, path, s3_path+"/"+bucket+"/"+path)
                if "train_repo_id" in pipe and isinstance(pipe["train_repo_id"], list):
                    for repo_id in pipe["train_repo_id"]:
                        self.train_repo_ids.append(str(repo_id))
                pipe_json.append(pipe)
        # 将列表转换为 JSON 格式的字符串
        pipe_json_str = json.dumps(pipe_json, ensure_ascii=False)

        # 打开文件并写入 JSON 格式的列表内容
        with open(os.path.join(self.output_path, "pipe.json"), 'w') as f:
            f.write(pipe_json_str)

    def export_repo(self):
        self.export_pipeline_template()
        self.__export_train_repo()
        # 将列表转换为 JSON 格式的字符串
        json_str = json.dumps(self.repo_json, ensure_ascii=False)

        # 打开文件并写入 JSON 格式的列表内容
        with open(os.path.join(self.output_path, "repo.json"), 'w') as f:
            f.write(json_str)

        print("printing compressed package, please wait a moment")
        zip_files_with_password(self.output_path, self.file_name, self.password)
        print("printing compressed package successfully")
        shutil.rmtree(self.output_path)

    def __export_train_repo(self):
        self.train_repo_ids = list(set(self.train_repo_ids))
        for repo_id in self.train_repo_ids:
            download_repo_info = self.__download_train_repo_by_id(repo_id)
            self.repo_json[repo_id] = download_repo_info
            if self.pack_image and "image" in download_repo_info:
                images = download_repo_info["image"]
                self.image.append(download_repo_info["image"])
                pull_docker_images_if_not_present(images)

        self.__save_docker()

    def __save_docker(self):
        if self.pack_image:
            output_file = 'image.tar'
            # 构建 Docker save 命令参数列表
            save_args = ['docker', 'save', '-o', os.path.join(self.output_path, output_file)] + self.image
            # 调用 Docker 命令保存多个镜像为 tar 文件
            proc = subprocess.Popen(save_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            # 输出保存日志
            if proc.returncode == 0:
                print('Docker images saved to {} successfully.'.format(output_file))
            else:
                print('Docker save failed. Error message:\n', err.decode('utf-8'))
                raise Exception('Docker save failed. Error message:\n', err.decode('utf-8'))

    def __export_data(self, dataset_ids, output_path):
        if not dataset_ids or len(dataset_ids) == 0:
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path, 0o0755, True)

        for name_version, dataset_id in dataset_ids.items():
            # 加metaloop的原因是导入abaddon之后，生成目录是会删除metaloop目录
            dataset_path = os.path.join(output_path, name_version, "metaloop")
            os.makedirs(dataset_path, 0o0755, True)
            self.mds_client.export_annotated_data([dataset_id], dataset_path, unencrypted=True)

    def __download_train_repo_by_id(self, repo_id):
        base_path = self.output_path
        s3_path = os.path.join(base_path, "s3_path")
        dataset_path = os.path.join(base_path, "dataset_path/" + str(repo_id))
        os.makedirs(dataset_path, 0o0755, True)
        post_data = {
            "id": int(repo_id),
            "limit": 1
        }
        resp_train_repos = self.mds_client.search_train_task_template(post_data)
        if len(resp_train_repos) == 0:
            raise Exception(f"train repo {repo_id} not found")
        resp_train_repo = resp_train_repos[0]
        repo_name = os.path.join(base_path, resp_train_repo["name"])
        os.makedirs(repo_name, 0o0755, True)
        repo = resp_train_repo["versions"][0]
        if "coverage" in repo and repo["coverage"] != "":
            url = parse.urlparse(repo["coverage"])
            coverage_path = s3_path + os.path.dirname(url.path)
            if not os.path.exists(coverage_path):
                os.makedirs(coverage_path)
            urlretrieve(repo["coverage"], s3_path + url.path)
            repo["coverage"] = url.path

        dataset_relation = {}
        dataset_ids = []
        if "test_dataset_ids" in repo:
            name_ids = {}
            for did in repo["test_dataset_ids"]:
                sp = did.split('?')
                if len(sp) > 1:
                    if sp[0] in dataset_relation:
                        dataset_relation[sp[0]].append("test")
                    else:
                        dataset_relation[sp[0]] = ["test"]
                    if sp[0] not in dataset_ids:
                        dataset_ids.append(sp[0])
                        name_ids[sp[0]] = sp[1]
            self.__export_data(name_ids, dataset_path)

        if "train_dataset_ids" in repo:
            name_ids = {}
            for did in repo["train_dataset_ids"]:
                sp = did.split('?')
                if len(sp) > 1:
                    if sp[0] in dataset_relation:
                        dataset_relation[sp[0]].append("train")
                    else:
                        dataset_relation[sp[0]] = ["train"]
                    if sp[0] not in dataset_ids:
                        dataset_ids.append(sp[0])
                        name_ids[sp[0]] = sp[1]
            self.__export_data(name_ids, dataset_path)

        if "train_code" in repo:
            train_path = repo["train_code"][1:]
            index = train_path.index('/')
            bucket = train_path[:index]
            path = train_path[index + 1:]
            self.mds_client.download_files_from_s3_storage(bucket, path, os.path.join(s3_path, train_path))

        if "model_config" in repo:
            model_config_str = repo["model_config"]
            model_config = json.loads(model_config_str)
            if "default" in model_config:
                plant_id = str(model_config["default"])
                plant = model_config[plant_id]
                if "abaddonlist" in plant:
                    dataset_id = plant["abaddonlist"]
                    dataset = self.mds_client.get_dataset_by_id(dataset_id)
                    name_version = f'{dataset.name}_V{dataset.version}'
                    if name_version in dataset_relation:
                        dataset_relation[name_version].append("model_test")
                    else:
                        dataset_relation[name_version] = ["model_test"]
                    if name_version not in dataset_ids:
                        dataset_ids.append(name_version)
                        name_ids = {name_version: dataset_id}
                        self.__export_data(name_ids, dataset_path)
        repo["dataset_relation"] = dataset_relation
        return repo


if __name__ == '__main__':
    args = parse_args()
    TrainRepoExport(args.user_token, args.api_addr, args.export_file_name, args.train_repo_ids,
                    args.pipe_template_ids, args.pack_image, args.password).export_repo()