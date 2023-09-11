import multiprocessing
import sys
from tqdm import tqdm
from asyncio import wait
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future, wait, FIRST_EXCEPTION
from typing import Dict, List

from botocore.client import BaseClient

from metaloop.client.x_api import X_API
from metaloop.client.cloud_storage import CloudClient, Job


class DownloadHelper:
    def __init__(
            self,
            x_api: X_API,
            batch_size: int = 1
    ):
        threads = min(16, multiprocessing.cpu_count())
        self._executor = ProcessPoolExecutor(threads) if sys.platform == "linux" else ThreadPoolExecutor(threads)
        self._client_map: Dict[str, BaseClient] = {}
        self._jobs: Dict[str, Job] = {}
        self._futures: List[Future] = []
        self._x_api = x_api
        self._batch_size = batch_size
        self._total = 0

    def _get_job(self, identifier: str) -> Job:
        if identifier not in self._jobs:
            self._jobs[identifier] = Job(len(self._jobs), identifier, [])
        return self._jobs[identifier]

    def download_s3_file(
            self,
            func,
            **kwargs
    ) -> str:
        identifier, item = func(**kwargs)

        job = self._get_job(identifier)
        job.batch.append(item)
        if len(job.batch) >= self._batch_size:
            self._futures.append(self._executor.submit(CloudClient.file_download_handler, job))
            self._jobs.pop(identifier)

        return item.obj_uri

    def download_http_file(
            self,
            func,
            **kwargs
    ) -> str:
        item = func(**kwargs)

        job = self._get_job("HTTP_FILE")
        job.batch.append(item)

        if len(job.batch) >= self._batch_size:
            self._futures.append(self._executor.submit(DownloadHelper.get_stream_data, self._x_api, job))
            self._jobs.pop("HTTP_FILE")

        return item.obj_uri

    def force_submit(self) -> None:
        for key, value in self._jobs.items():
            if key == "HTTP_FILE":
                self._futures.append(self._executor.submit(DownloadHelper.get_stream_data, self._x_api, value))
            else:
                self._futures.append(self._executor.submit(CloudClient.file_download_handler, value))

    def wait(self) -> None:
        # done, not_done = wait(self._futures, return_when=FIRST_EXCEPTION)
        # for future in not_done:
        #     future.cancel()
        # for future in done:
        #     future.result()
        for future in tqdm(self._futures):
            try:
                future.result()
            except Exception as exc:
                print('downloder generated an exception: %s' % (exc)) 

    @staticmethod
    def get_stream_data(x_api: X_API, job: Job):
        for item in job.batch:
            x_api.get_stream_data(item.key, item.file_name)
