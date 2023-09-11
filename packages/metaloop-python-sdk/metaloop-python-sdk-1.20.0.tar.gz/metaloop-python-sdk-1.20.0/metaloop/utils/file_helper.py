import os
import re
from typing import Dict, Tuple

import mimetypes

FileTypeVideo = "video"
FileTypeImage = "image"
FileTypeZip = "zip"
FileTypeDoc = "doc"
FileTypeAttachment = "attachment"

UPLOAD_FILE_TYPE: Dict[str, str] = {
    "jpg": FileTypeImage,
    "jpeg": FileTypeImage,
    "png": FileTypeImage,
    "gif": FileTypeImage,
    "npy": FileTypeImage,
    "mp4": FileTypeVideo,
    "avi": FileTypeVideo,
    "mpg": FileTypeVideo,
    "mpeg": FileTypeVideo,
    "3gp": FileTypeVideo,
    "mov": FileTypeVideo,
    "m4v": FileTypeVideo,
    "dat": FileTypeVideo,
    "mkv": FileTypeVideo,
    "flv": FileTypeVideo,
    "vob": FileTypeVideo,
    "dav": FileTypeVideo,
    "ts": FileTypeVideo,
    "md": FileTypeVideo,
    "h264": FileTypeVideo,
    "h265": FileTypeVideo,
    "zip": FileTypeZip,
    "gz": FileTypeZip,
    "tar": FileTypeZip,
    "rar": FileTypeZip,
    "bz2": FileTypeZip,
    "csv": FileTypeDoc,
    "json": FileTypeDoc,
    "pdf": FileTypeDoc,
    "txt": FileTypeDoc,
    "xml": FileTypeDoc,
}


def get_file_type(file_path: str) -> Tuple[str, str]:
    file_type = mimetypes.guess_type(file_path)[0]
    if not file_type:
        file_type = "application/octet-stream"

    name = os.path.basename(file_type)
    if name in UPLOAD_FILE_TYPE:
        upload_file_type = UPLOAD_FILE_TYPE[name]
    else:
        upload_file_type = FileTypeAttachment

    return file_type, upload_file_type


# OriginPathRegMode1 image/upload/20220420/zip/2532f439-dac7-4278-9e60-eeb51d4e7504/天津0406-0412回流数据1.tar/天津0406-0412回流数据1/a.jpg
OriginPathRegMode1 = r'(image|video|none)/upload/[\d]+/zip/[a-zA-z0-9-]+/[^/]+/(.+)'
# OriginPathRegMode2 /abaddon/video/upload/20220715/video/1467eb79-0913-48c6-a0d3-8d487e7a00a3/0714_3000_w54.mp4.mp4
OriginPathRegMode2 = r'(image|video|none)/upload/[\d]+/(image|video)/[^/]+/(.+)'
# OriginPathRegMode3 image/upload/20211008/03a8f57b-214b-4126-bc56-749c9f316f28.jpg
OriginPathRegMode3 = r'(image|video|none)/upload/[\d]+/(.+)'
# OriginPathRegMode4 /abaddon/raw/20211110154700/deepglint_video_20210705/现金/background_0_f1621f8a-5bd8-4c9b-b89b-67f5febdd756.jpg
OriginPathRegMode4 = r'(raw|baidu)/[^/]+/(.+)'
OriginPathRegMode5 = r'(raw|baidu|image|video|none)/(.+)'
OriginPathRegMode6 = r'^[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}/(.+)'


def get_user_origin_path(object_name: str) -> str:
    match = re.match(OriginPathRegMode6, object_name)
    if match:
        return match[2]
    match = re.match(OriginPathRegMode1, object_name)
    if match:
        return match[2]
    match = re.match(OriginPathRegMode2, object_name)
    if match:
        return match[3]
    match = re.match(OriginPathRegMode3, object_name)
    if match:
        return match[2]
    match = re.match(OriginPathRegMode4, object_name)
    if match:
        return match[2]
    match = re.match(OriginPathRegMode5, object_name)
    if match:
        return match[2]
    return object_name


def get_bucket_and_key(url: str) -> (str, str):
    url = url.rstrip("/")
    if url.startswith("/"):
        index = url[1:].find("/")
        if index > -1:
            return url[1:index + 1], url[index + 2:]
    return "abaddon", url.strip("/")
