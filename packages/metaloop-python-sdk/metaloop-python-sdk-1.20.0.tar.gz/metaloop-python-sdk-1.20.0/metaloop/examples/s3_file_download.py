import io
import time

from metaloop.client import MDS, CloudConfig, CloudClient


def get_cloud_storage_config(
        x_api,
        name: str,
        storage_type: str = ""
) -> CloudConfig:
    if not CloudClient.find_s3_config(name):
        info = x_api.get_authorized_s3_config(name, storage_type)
        identifier = info["name"]
        endpoint = info["endpoint"]
        access_key = info["access_key"]
        secret_key = info["secret_key"]
        default_bucket = info["bucket"]

        CloudClient.set_s3_config(identifier, endpoint, access_key, secret_key, default_bucket)
    else:
        identifier = name

    return CloudClient.find_s3_config(identifier)


if __name__ == '__main__':
    mds_client = MDS("d00b1b90-7b3c-4208-b270-d65a654f22d5")
    file_list = ['/abaddon/image/upload/20221027/zip/dc32a6af-13c7-4308-9f52-283be05930c2/shoot_20220808_3 2/shoot_20220808_3 2/shoot_20220808_3/shoot1.jpg']
    index = 0
    for url in file_list:
        if url.startswith('/'):
            items = url.strip("/").split("/")
            bucket = items[0]
            key = '/'.join(items[1:])
            s3_config = get_cloud_storage_config(mds_client.x_api, bucket)
            # with open(str(index)+'.jpg', 'wb') as data:
            #     CloudClient.download_fileobj(s3_config.identifier, bucket, key, data)

            bytes_buffer = io.BytesIO()
            CloudClient.download_fileobj(s3_config.identifier, bucket, key, bytes_buffer)

        else:
            s3_config = get_cloud_storage_config(mds_client.x_api, 'local')
            with open(str(index) + '.jpg', 'wb') as data:
                CloudClient.download_fileobj(s3_config.identifier, s3_config.default_bucket, url, data)
        index += 1
