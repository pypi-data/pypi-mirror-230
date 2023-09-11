"""Related classes for the Cloud Storage."""
import multiprocessing
import os
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait, FIRST_EXCEPTION
from typing import Dict, Optional, Union, List

import boto3
from boto3 import Session
from boto3.s3.transfer import TransferConfig
from botocore import UNSIGNED
from botocore.client import BaseClient
from botocore.config import Config
from tqdm import tqdm

from metaloop.client.x_api import X_API
from metaloop.exception import ResourceNotExistError, AccessDeniedError, ClientError


class CloudConfig:
    def __init__(
        self,
        identifier: str,
        endpoint: str,
        access_key_id: str,
        secret_access_key: str,
        default_bucket: Optional[str] = ""
    ) -> None:
        self._identifier = identifier
        self._endpoint = endpoint
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._default_bucket = default_bucket

    @property
    def identifier(self):
        return self._identifier

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def access_key_id(self):
        return self._access_key_id

    @property
    def secret_access_key(self):
        return self._secret_access_key

    @property
    def default_bucket(self):
        return self._default_bucket


class Item:
    def __init__(
            self,
            bucket: str,
            key: str,
            file_name: str,
            obj_uri: str = ""
    ) -> None:
        self.bucket = bucket
        self.key = key
        self.file_name = file_name
        self.obj_uri = obj_uri


class Job:
    def __init__(
            self,
            job_id: int,
            identifier: str,
            batch: List[Item]
    ) -> None:
        self.job_id = job_id
        self.identifier = identifier
        self.batch = batch


_CLOUD_CONFIG: Dict[str, CloudConfig] = {}
_CLOUD_SESSION: Dict[str, Session] = {}


class CloudClient:
    """:class:`CloudClient` defines the client to interact with cloud storage.
    """

    @staticmethod
    def _get_client(
            identifier: str,
            validate: Optional[bool] = False
    ) -> BaseClient:
        try:
            config = _CLOUD_CONFIG[identifier]
        except KeyError as error:
            raise ResourceNotExistError(resource="cloud_config", identification=identifier) from error

        try:
            session = _CLOUD_SESSION[identifier]
        except KeyError:
            session = boto3.Session(config.access_key_id, config.secret_access_key)
            _CLOUD_SESSION[identifier] = session

        if not config.access_key_id:
            client = session.client(service_name="s3", endpoint_url=config.endpoint, config=Config(signature_version=UNSIGNED))
        else:
            client = session.client(service_name="s3", endpoint_url=config.endpoint)

        if validate:
            try:
                client.list_buckets()
            except ClientError as error:
                raise AccessDeniedError(message="fail to connect to s3 endpoint") from error

        return client

    @staticmethod
    def get_default_bucket(identifier: str):
        try:
            config = _CLOUD_CONFIG[identifier]
        except KeyError as error:
            raise ResourceNotExistError(resource="cloud_config", identification=identifier) from error

        return config.default_bucket

    @staticmethod
    def find_s3_config(identifier: str) -> Union[CloudConfig, None]:
        if identifier in _CLOUD_CONFIG:
            return _CLOUD_CONFIG[identifier]
        return None

    @staticmethod
    def set_s3_config(
        identifier: str,
        endpoint: str,
        access_key_id: str,
        secret_access_key: str,
        default_bucket: str
    ) -> None:
        config = CloudConfig(identifier, endpoint, access_key_id, secret_access_key, default_bucket)
        _CLOUD_CONFIG[identifier] = config

    @staticmethod
    def get_cloud_storage_config(
            x_api: X_API,
            name: str,
            storage_type: Optional[str] = ""
    ) -> CloudConfig:
        if not name:
            name = storage_type

        if not CloudClient.find_s3_config(name):
            info = x_api.get_authorized_s3_config(name, storage_type)
            identifier = info["name"]
            endpoint = info["endpoint"]
            access_key = info["access_key"]
            secret_key = info["secret_key"]
            default_bucket = info["bucket"]

            CloudClient.set_s3_config(identifier, endpoint, access_key, secret_key, default_bucket)
            if name != default_bucket:
                CloudClient.set_s3_config(default_bucket, endpoint, access_key, secret_key, default_bucket)
        else:
            identifier = name

        return CloudClient.find_s3_config(identifier)

    @staticmethod
    def upload_file(
            identifier: str,
            bucket: str,
            file_path: str,
            upload_prefix: Optional[str] = ""
    ) -> str:
        object_name = os.path.join(upload_prefix, os.path.basename(file_path))

        client = CloudClient._get_client(identifier)
        with tqdm(unit="MB", unit_scale=1) as pbar:
            config = TransferConfig(max_concurrency=16)
            client.upload_file(file_path,
                               bucket,
                               object_name,
                               Config=config,
                               Callback=UploadProgress(file_path, pbar))

        return os.path.join("/" + bucket, object_name)

    @staticmethod
    def upload_files(
            identifier: str,
            bucket: str,
            file_path: str,
            upload_prefix: Optional[str] = ""
    ) -> str:
        client = CloudClient._get_client(identifier)

        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)

        file_path = file_path.rstrip("/")
        index = len(os.path.dirname(file_path))

        if not upload_prefix:
            date_time = time.strftime("%Y%m%d", time.localtime())
            upload_prefix = f"raw/{date_time}"

        for root, dirs, files in tqdm(os.walk(file_path)):
            prefix = root[index:].strip("/")
            prefix = os.path.join(upload_prefix, prefix)
            for item in files:
                client.upload_file(os.path.join(root, item), bucket, os.path.join(prefix, item))

        return os.path.join("/", bucket, upload_prefix, os.path.basename(file_path))

    @staticmethod
    def upload_files_parallel(
            identifier: str,
            bucket: str,
            file_path: str,
            upload_prefix: Optional[str] = "",
            batch_size: Optional[int] = 64,
            thread_num: Optional[int] = 16
    ) -> str:
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)

        file_path = file_path.rstrip("/")
        index = len(os.path.dirname(file_path))

        batch = []
        count = 0
        futures = []
        threads = min(thread_num, multiprocessing.cpu_count())
        with (ProcessPoolExecutor(threads) if sys.platform == "linux" else ThreadPoolExecutor(threads)) as executor:
            for root, dirs, files in os.walk(file_path):
                prefix = root[index:].strip("/")
                prefix = os.path.join(upload_prefix, prefix)

                for item in files:
                    batch.append(Item(bucket, os.path.join(prefix, item), os.path.join(root, item)))
                    count += 1

                    if count % batch_size == 0:
                        futures.append(executor.submit(CloudClient.file_upload_handler, (Job(count, identifier, batch))))
                        batch = []

            if len(batch) > 0:
                futures.append(executor.submit(CloudClient.file_upload_handler, (Job(count, identifier, batch))))

            done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
            for future in not_done:
                future.cancel()
            for future in done:
                future.result()

        return os.path.join("/", bucket, upload_prefix, os.path.basename(file_path))

    @staticmethod
    def file_upload_handler(job: Job):
        client = CloudClient._get_client(job.identifier)
        for item in job.batch:
            client.upload_file(item.file_name, item.bucket, item.key)

    @staticmethod
    def download_file(
            identifier: str,
            bucket: str,
            key: str,
            file_path: str,
            image_path: Optional[str] = ""
    ) -> str:
        if not file_path:
            file_path = "abaddon"

        if image_path:
            image_path = image_path.strip("/")
            file_name = os.path.join(file_path, image_path)
        else:
            file_name = os.path.join(file_path, key)

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), 0o0755)

        client = CloudClient._get_client(identifier)
        client.download_file(bucket, key, file_name)

        return image_path if image_path else key

    @staticmethod
    def download_fileobj(
            identifier: str,
            bucket: str,
            key: str,
            fileobj
    ):
        client = CloudClient._get_client(identifier)
        client.download_fileobj(Bucket=bucket, Key=key, Fileobj=fileobj)

    @staticmethod
    def download_files(
            identifier: str,
            bucket: str,
            prefix: str,
            file_path: str
    ) -> str:
        client = CloudClient._get_client(identifier)
        for item in CloudClient._list_all_objects(client, Bucket=bucket, Prefix=prefix):
            key = item["Key"]
            if key.endswith("/"):
                continue

            file_name = os.path.join(file_path, key)
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name), 0o0755)

            client.download_file(bucket, key, file_name)

        return os.path.join(file_path, prefix)

    @staticmethod
    def download_files_parallel(
            identifier: str,
            bucket: str,
            prefix: str,
            file_path: str,
            batch_size: Optional[int] = 128,
            thread_num: Optional[int] = 16
    ) -> str:
        client = CloudClient._get_client(identifier)
        batch = []
        count = 0
        futures = []
        threads = min(thread_num, multiprocessing.cpu_count())
        with (ProcessPoolExecutor(threads) if sys.platform == "linux" else ThreadPoolExecutor(threads)) as executor:
            for item in CloudClient._list_all_objects(client, Bucket=bucket, Prefix=prefix):
                key = item["Key"]
                if key.endswith("/"):
                    continue

                # prefix 是文件
                file_name = file_path
                path = key[len(prefix.rstrip('/')) + 1:]
                # prefix 是文件夹
                if path != "":
                    file_name = os.path.join(file_path, path)
                if not os.path.exists(os.path.dirname(file_name)):
                    os.makedirs(os.path.dirname(file_name), 0o0755)

                batch.append(Item(bucket, key, file_name))

                count += 1
                if count % batch_size == 0:
                    futures.append(executor.submit(CloudClient.file_download_handler, (Job(count, identifier, batch))))
                    batch = []

            if len(batch) > 0:
                futures.append(executor.submit(CloudClient.file_download_handler, (Job(count, identifier, batch))))

            done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
            for future in not_done:
                future.cancel()
            for future in done:
                future.result()

        return os.path.join(file_path, prefix)

    @staticmethod
    def file_download_handler(job: Job):
        client = CloudClient._get_client(job.identifier)
        for item in job.batch:
            client.download_file(item.bucket, item.key, item.file_name)

    @staticmethod
    def _list_all_objects(client: BaseClient, **base_kwargs):
        continuation_token = None
        while True:
            list_kwargs = dict(MaxKeys=1000, **base_kwargs)
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token
            response = client.list_objects_v2(**list_kwargs)

            yield from response.get("Contents", [])
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")


class UploadProgress(object):
    def __init__(self, filename, pbar):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._pbar = pbar
        self._pbar.reset(self._size * 1e-6)

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            if self._seen_so_far < self._size:
                self._pbar.update(bytes_amount * 1e-6)
