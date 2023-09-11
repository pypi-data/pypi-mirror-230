import json
import os.path
from typing import Dict, Any, Optional, List
from urllib import parse

from requests.models import Response
from requests_toolbelt import MultipartEncoder
from s3transfer.constants import MB

from metaloop.client.requests import Client
from metaloop.exception import ResourceNotExistError, InvalidParamsError, InternalServerError


class X_API:
    def __init__(self, client: Client):
        self._client = client

    def create_dataset(
            self,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("POST", "", json=post_data).json()
        return response["data"][0]

    def pretrain_callback_task(
            self,
            task_id: str,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("POST", f"pretrain/task/{task_id}/callback", json=post_data).json()
        return response
    
    def leader_board_callback_task(
            self,
            task_id: str,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("POST", f"leaderboard/task/{task_id}/callback", json=post_data).json()
        return response

    def delete_dataset(
            self,
            dataset_id: str
    ) -> None:
        self._client.open_api_do("DELETE", "", dataset_id)

    def get_version(
            self,
            dataset_id: str
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("GET", "", dataset_id).json()

        try:
            info = response["data"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="dataset", identification=dataset_id) from error

        return info

    def get_dataset(
            self,
            name: str,
            **kwargs
    ) -> Dict[str, Any]:
        if not name:
            raise InvalidParamsError(param_name="dataset", param_value=name)

        response = self.list_datasets(name=name, **kwargs)

        try:
            info = response["data"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="dataset", identification=name) from error

        return info

    def exist_dataset(
            self,
            name: str,
    ) -> bool:
        if not name:
            raise InvalidParamsError(param_name="dataset", param_value=name)

        response = self.list_datasets(name=name)
        if "data" in response:
            return len(response['data']) != 0

        return False

    def get_dataset_name(
            self,
            name: str,
    ) -> Dict[str, Any]:
        if not name:
            raise InvalidParamsError(param_name="dataset", param_value=name)

        response = self.list_dataset_name(name=name, accurate=True)

        try:
            info = response["data"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="dataset", identification=name) from error

        return info

    def list_datasets(
            self,
            name: Optional[str] = None,
            offset: int = 0,
            limit: int = 128,
            **kwargs
    ) -> Dict[str, Any]:
        post_data: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }
        post_data.update(kwargs)
        if name:
            post_data["name"] = [name]

        response = self._client.open_api_do("POST", "search/dataset", json=post_data)
        return response.json()

    def list_dataset_name(
            self,
            name: Optional[str] = None,
            accurate: Optional[bool] = False,
            offset: int = 0,
            limit: int = 128
    ) -> Dict[str, Any]:
        post_data: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }
        if name:
            post_data["name"] = name

        if accurate:
            post_data["accurate"] = True

        response = self._client.open_api_do("POST", "search/dataset/name", json=post_data)
        return response.json()

    def get_space(self, name: str) -> Dict[str, Any]:
        if not name:
            raise InvalidParamsError(param_name="space", param_value=name)

        response = self.list_spaces(name=name)

        try:
            info = response["data"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="space", identification=name) from error

        return info

    def list_spaces(
            self,
            name: Optional[str] = None,
            offset: int = 0,
            limit: int = 128,
    ) -> Dict[str, Any]:
        post_data: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }
        if name:
            post_data["name"] = [name]

        response = self._client.open_api_do("POST", "search/space", json=post_data)
        return response.json()

    def get_tag(self, name: str) -> Dict[str, Any]:
        if not name:
            raise InvalidParamsError(param_name="tag", param_value=name)

        try:
            response = self.list_tags(name=name)
            info = response["data"][0]
        except IndexError as error:
            raise ResourceNotExistError(resource="tag", identification=name) from error

        return info

    def list_tags(
            self,
            name: Optional[str] = None,
            offset: int = 0,
            limit: int = 128,
    ) -> Dict[str, Any]:
        post_data: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
            "accurate": True
        }
        if name:
            post_data["name"] = [name]

        response = self._client.open_api_do("POST", "search/tag", json=post_data)
        return response.json()

    def list_objects(
            self,
            dataset_id: str,
            offset: int = 0,
            limit: int = 128,
    ) -> Dict[str, Any]:
        post_data: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
            "dataset_id": [dataset_id]
        }

        response = self._client.open_api_do("POST", "search/dataset/object", json=post_data)
        return response.json()

    def get_dataset_path(
            self,
            dataset_id: str,
            path: Optional[str] = ""
    ) -> str:
        path_root = self.get_dataset_path_root(dataset_id)
        prefix = os.path.join(path_root, path.strip("/")).rstrip("/")
        file_path = os.path.dirname(prefix)
        base_name = os.path.basename(prefix)

        params: Dict[str, Any] = {"prefix": file_path}
        response = self._client.open_api_do("GET", "path", dataset_id, params=params).json()

        if base_name not in response["data"]:
            raise ResourceNotExistError(resource="path", identification=path)

        return prefix[len(dataset_id) + 1:]

    def get_dataset_path_root(
            self,
            dataset_id: str
    ) -> str:
        response = self._client.open_api_do("GET", "path", dataset_id).json()

        try:
            path_root = os.path.dirname(response["data"][0])
        except IndexError as error:
            raise ResourceNotExistError(resource="dataset path root", identification=dataset_id) from error

        return path_root

    def get_authorized_s3_config(
            self,
            name: Optional[str] = "",
            storage_type: Optional[str] = ""
    ) -> Dict[str, Any]:
        if not name and not storage_type:
            raise InvalidParamsError(message="name and type of cloud storage need at least one")

        bucket_or_type = ''
        if name:
            bucket_or_type = name
        elif storage_type:
            bucket_or_type = storage_type

        response = self._client.open_api_do("GET", "api_s3_storage_config?bucket=" + bucket_or_type).json()

        try:
            s3_resp = response["data"]["s3"]
            s3_parsed = parse.urlparse(s3_resp)
            query = parse.parse_qs(s3_resp)
            endpoint = 'http://'
            if 'sslmode' in query and query['sslmode'] == "enable":
                endpoint = 'https://'
            endpoint = endpoint + s3_parsed.hostname
            if s3_parsed.port is not None and s3_parsed.port != 80:
                endpoint = endpoint + ":" + str(s3_parsed.port)
            info: Dict[str, Any] = {
                "name": bucket_or_type,
                "endpoint": endpoint,
                "access_key": s3_parsed.username,
                "bucket": s3_parsed.path.strip('/'),
                "secret_key": s3_parsed.password
            }
        except IndexError:
            raise ResourceNotExistError(resource="cloud storage config", identification=f"{name}({storage_type})")

        return info

    def merge_dataset(
            self,
            dataset_id: str,
            merged_dataset_ids: List[str]
    ) -> None:
        post_data: Dict[str, Any] = {
            "dataset_id": merged_dataset_ids
        }
        self._client.open_api_do("POST", "merge", dataset_id, json=post_data)

    def post_import(
            self,
            dataset_id: str,
            post_data: str
    ) -> None:
        self._client.open_api_do("POST", "import", dataset_id, json=post_data, params={"env": "dataset_transfer"})

    def get_import_status(
            self,
            dataset_id: str
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("GET", "import", dataset_id, params={"env": "dataset_transfer"}).json()

        try:
            info = response["data"][0]
        except IndexError as error:
            raise InternalServerError(message="cannot get import status from server") from error

        return info

    def post_export(
            self,
            dataset_id: str,
            post_data: str
    ) -> str:
        response = self._client.open_api_do("POST", "export", dataset_id, json=post_data).json()

        try:
            info = response["data"]
        except KeyError as error:
            raise InternalServerError(message="cannot get export status from server") from error

        try:
            return info["task_id"]
        except TypeError:
            return ""

    def post_export_multi(
            self,
            dataset_id: str,
            post_data: str
    ) -> str:
        response = self._client.open_api_do("POST", "export/multi", dataset_id, json=post_data).json()

        try:
            info = response["data"]
        except KeyError as error:
            raise InternalServerError(message="cannot get export status from server") from error

        try:
            return info["task_id"]
        except TypeError:
            return ""

    def get_export_status(
            self,
            dataset_id: str,
            task_id: str
    ) -> Dict[str, Any]:
        if task_id:
            response = self._client.open_api_do("GET", os.path.join("export", task_id), dataset_id).json()
        else:
            response = self._client.open_api_do("GET", "export", dataset_id).json()

        try:
            info = response["data"][0]
        except IndexError as error:
            raise InternalServerError(message="cannot get export status from server") from error

        return info

    def get_export_catalog(
            self,
            url: str
    ) -> List[str]:
        response = self.get_input_json(url)
        lines = self.read_lines(response)
        for retryTimes in range(3):
            if self.check_completion(response):
                break
            print(self.get_retry_str(retryTimes))
            response = self.get_input_json(url)
            lines = self.read_lines(response)

        export_list: List[Any] = []
        for line in lines:
            export_list.append(json.loads(line))

        return export_list

    def get_retry_str(self, retry: int) -> str:
        retry_str = ''
        if retry + 1 == 1:
            retry_str = '1st'
        elif retry + 1 == 2:
            retry_str = '2nd'
        elif retry + 1 == 3:
            retry_str = '3rd'
        else:
            retry_str = str(retry) + 'th'
        return 'retry {} time ...'.format(retry_str)

    def check_completion(self, response: Response) -> bool:
        content_len = int(response.headers.get("Content-Length"))
        actual_len = response.raw.tell()
        if actual_len != content_len:
            print('Response Content-Length {} vs actual reading length {}'.format(content_len, actual_len))
            return False
        return True

    def read_lines(self, response: Response) -> List[str]:
        lines: List[str] = []
        for line in response.iter_lines(chunk_size=1 * MB):
            lines.append(line)
        return lines

    def get_input_json(self, url: str) -> Response:
        if url.find("abaddonapi") > -1:
            section = url.split("abaddonapi/v1/")[1]
            response = self._client.open_api_do("GET", section, "", stream=True, timeout=3600)
        elif url.find("abaddon-service") > -1:
            section = url.split("abaddon-service/v1/")[1]
            response = self._client.open_api_do("GET", section, "", stream=True, timeout=3600)
        else:
            response = self._client.do("GET", url, timeout=3600)
        return response

    def post_multipart_formdata(
            self,
            data: Dict[str, Any]
    ) -> str:
        multipart = MultipartEncoder(data)

        try:
            response = self._client.open_api_do(
                "POST",
                "upload",
                data=multipart,
                params={"env": "dataset_transfer"},
                headers={"Content-Type": multipart.content_type},
            ).json()
            info = response["data"][0]
        except IndexError as error:
            raise InternalServerError(message="cannot get upload status from server") from error

        return info["upload_id"]

    def get_stream_data(
            self,
            url: str,
            file_path: str
    ) -> None:
        response = self._client.open_api_do("GET", url, "", stream=True)

        with open(file_path, "wb") as f:
            for ch in response:
                f.write(ch)
            f.close()

    def call_model_convert_path_status(
            self,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("PUT", "model_convert/path/callback", "", json=post_data).json()
        return response

    def call_model_test_status(
            self,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("PUT", "model_test/status/callback", "", json=post_data).json()
        return response

    def call_model_test_result_content(
            self,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("PUT", "model_test_result/content/callback", "", json=post_data).json()
        return response

    def send_notice(
            self,
            title: str,
            status: int,
            msg: str,
            usernames: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        data = {}
        data["title"] = title
        data["status"] = status
        data["msg"] = msg
        if usernames:
            data["usernames"] = usernames
        response = self._client.open_api_do("POST", "notice", "", json=data).json()
        return response

    def update_algo_svc_test(self, id: int, status: Optional[str] = None, result: Optional[str] = None,
                             perfres: Optional[str] = None):
        data = {}
        data["id"] = id
        if status is not None:
            data["status"] = status
        if result is not None:
            data["result"] = result
        if perfres is not None:
            data["perfres"] = perfres
        api = "algo_svc_test"
        return self._client.open_api_do("PUT", api, json=data).json()

    def update_calibset(self,
                        id: int,
                        status: Optional[int] = None,
                        pb_url: Optional[str] = None,
                        log: Optional[str] = None,
                        folders: Optional[str] = None,
                        category: Optional[str] = "default"
                        ) -> Dict[str, Any]:
        data = {}
        data["id"] = id
        data["status"] = status
        data["pb_url"] = pb_url
        data["log"] = log
        data["folders"] = folders
        api = "model_calib?category=" + category
        response = self._client.open_api_do("PUT", api, "", json=data).json()
        return response

    def get_ppf_url_by_category(self, category: str) -> str:
        api = "ppf/lists?category=" + category
        response = self._client.open_api_do("GET", api, "").json()
        return response["data"]["path_url"]

    def search_train_task_template(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        api = "search/train_task_template"
        response = self._client.open_api_do("POST", api, "", json=post_data).json()
        return response["data"]

    def create_train_task_template(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        api = "train/task_template"
        response = self._client.open_api_do("POST", api, "", json=post_data).json()
        return response["data"]

    def get_pipe_template_by_id(self, id: str, export: bool) -> Dict[str, Any]:
        api = "pipeline_template/" + id
        if export:
            api += "?export=true"
        response = self._client.open_api_do("GET", api, "", ).json()
        return response["data"]

    def create_pipe_template(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        api = "pipeline_template"
        response = self._client.open_api_do("POST", api, "", json=post_data).json()
        return response["data"]

    def call_model_search_result(
            self,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("POST", "model_search/callback", "", json=post_data).json()
        return response

    def callback(
            self,
            callback_url: str,
            post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = self._client.open_api_do("POST", callback_url, "", json=post_data).json()
        return response


