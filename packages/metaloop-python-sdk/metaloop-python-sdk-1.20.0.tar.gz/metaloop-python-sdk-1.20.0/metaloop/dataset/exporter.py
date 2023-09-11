import json
from urllib.parse import urlparse

from metaloop.client.cloud_storage import *
from metaloop.client.download_helper import DownloadHelper
from metaloop.utils.file_helper import *


class Exporter:
    def __init__(self, x_api):
        self._x_api = x_api

    def get_data(self, catalog, file_path, storage_type):
        if not os.path.exists(file_path):
            os.makedirs(file_path, 0o0775)

        file_writer = open(os.path.join(file_path, "output.json.tmp"), "w")
        download_helper = DownloadHelper(self._x_api)

        count = 0
        for obj in catalog:
            count += 1
            ex = False
            image_path = obj["image_path"] if "image_path" in obj else ""

            if "external_url_image" in obj:
                # /{bucket}/{path}/{to}/{object}.ext
                url = obj["external_url_image"]

                items = url.strip("/").split("/")
                if len(items) < 2:
                    continue

                s3_config = CloudClient.get_cloud_storage_config(self._x_api, items[0], storage_type=storage_type)

                file_name = download_helper.download_s3_file(
                    self._download_file,
                    identifier=s3_config.identifier,
                    bucket=items[0],
                    url=url,
                    file_path=file_path,
                    image_path=image_path
                )
                obj["url_image"] = file_name
                ex = True

            if not ex:
                # {endpoint}/{bucket}/{path}/{to}/{object}.ext
                url = str(obj["url_image"])
                file_name = download_helper.download_http_file(
                    self._download_http_file,
                    url=url,
                    file_path=file_path,
                    image_path=image_path
                )
                obj["url_image"] = file_name

            body = json.dumps(obj, ensure_ascii=False)
            file_writer.write(body)
            file_writer.write("\n")
            if not count % 128:
                file_writer.flush()

        download_helper.force_submit()
        download_helper.wait()

        file_writer.flush()
        file_writer.close()
        os.rename(os.path.join(file_path, "output.json.tmp"), os.path.join(file_path, "output.json"))

    @staticmethod
    def _download_file(
            **kwargs
    ) -> Tuple[str, Item]:
        key, file_name, obj_url = Exporter._get_download_info(
            kwargs["url"],
            kwargs["file_path"],
            kwargs["image_path"]
        )
        return kwargs["identifier"], Item(kwargs["bucket"], key, file_name, obj_url)

    @staticmethod
    def _download_http_file(
            **kwargs
    ) -> Item:
        _, file_name, obj_url = Exporter._get_download_info(
            urlparse(kwargs["url"]).path,
            kwargs["file_path"],
            kwargs["image_path"]
        )
        return Item("", kwargs["url"], file_name, obj_url)

    @staticmethod
    def _get_download_info(
            url: str,
            file_path: str,
            image_path: str
    ) -> Tuple[str, str, str]:
        _, key = get_bucket_and_key(url)

        if not image_path:
            image_path = get_user_origin_path(key)

        if not file_path or image_path.find("/") < 0:
            image_path = os.path.join("abaddon", image_path)

        file_name = os.path.join(file_path, image_path.strip("/"))

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), 0o0755)

        while file_path.endswith('/'):
            file_path = file_path[:-1]

        obj_url = file_name[len(file_path) + 1:]

        return key, file_name, obj_url

    def _download_files(
            self,
            bucket: str,
            prefix: str,
            file_path: str
    ) -> str:
        s3_config = CloudClient.get_cloud_storage_config(self._x_api, bucket)
        return CloudClient.download_files_parallel(s3_config.identifier, bucket, prefix, file_path)

    def _get_stream_data(
            self,
            url: str,
            file_path: str
    ) -> str:
        if url.startswith("http://"):
            file_name = url[url.index("http://") + 7:]
        elif url.startswith("https://"):
            file_name = url[url.index("https://") + 8:]
        else:
            file_name = url

        index = file_name.find("/")
        if index > -1:
            file_name = os.path.join(file_path, file_name[index + 1:])
        else:
            file_name = os.path.join(file_path, file_name)

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), 0o0755)

        self._x_api.get_stream_data(url, file_name)

        return url[index + 8:]
