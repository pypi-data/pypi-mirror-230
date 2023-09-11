import argparse

from metaloop.client import MDS


def parse_args():
    parser = argparse.ArgumentParser(description='export and download data from metaloop')
    parser.add_argument('--api_addr', required=True, help='address of metaloop API')
    parser.add_argument('--user_token', required=True, help='user token used to access metaloop API')
    parser.add_argument('--bucket', required=True, help='bucket of s3 storage')
    parser.add_argument('--prefix', required=True, help='prefix of s3 storage object')
    parser.add_argument('--output_path', default='', help='local path to store downloaded data')
    return parser.parse_args()


def main(args):
    mds_client = MDS(args.user_token, args.api_addr)
    mds_client.download_files_from_s3_storage(args.bucket, args.prefix, args.output_path, storage_type="local")


if __name__ == '__main__':
    args = parse_args()
    main(args)
