import os

import os
import zipfile

import pyzipper


def zip_files_with_password(file_path, archive_path, password=str):
    with pyzipper.AESZipFile(archive_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
        zipf.setpassword(password.encode())
        for root, dirs, files in os.walk(file_path):
            for file in files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, os.path.dirname(file_path))
                zipf.write(path, arcname=rel_path)
    print(f"Files compressed to {archive_path} with password {password}")


def unzip_file(zip_filename, password=str, extract_path='.'):
    with pyzipper.AESZipFile(zip_filename, 'r') as zipf:
        zipf.setpassword(password.encode())
        zipf.extractall(extract_path)

