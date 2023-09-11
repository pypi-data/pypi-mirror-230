import argparse
import os.path
import json

from metaloop.client.mds import MDS


def parse_args():
    parser = argparse.ArgumentParser(description='export and download data from metaloop')
    parser.add_argument('--api_addr', required=True, help='address of metaloop API')
    parser.add_argument('--user_token', required=True, help='user token used to access metaloop API')
    parser.add_argument('--train_dataset_ids', required=True, help='IDs of training dataset to export')
    parser.add_argument('--test_dataset_ids', default='', help='IDs of test dataset to export')
    parser.add_argument('--online_dataset_ids', default='', help='IDs of online dataset to export')
    parser.add_argument('--output_path', default='', help='local path to store downloaded data')
    return parser.parse_args()


def get_data(mds_client, dataset_ids, flag='train'):
    if not dataset_ids:
        return

    output_path = os.path.join(args.output_path, flag)
    if not os.path.exists(output_path):
        os.makedirs(output_path, 0o0755, True)

    mds_client.export_annotated_data(dataset_ids.split(','), output_path)
    if os.path.exists(os.path.join(output_path, 'output.json')):
        file_out = open(os.path.join(output_path, 'input.json'), 'w')
        with open(os.path.join(output_path, 'output.json'), 'r') as f:
            for line in f:
                data = json.loads(line)
                data['url_image'] = os.path.join(output_path, data['url_image'])
                json.dump(data, file_out, ensure_ascii=False)
                file_out.write('\n')
        file_out.close()
        os.remove(os.path.join(output_path, 'output.json'))


def main(args):
    mds_client = MDS(args.user_token, args.api_addr)

    get_data(mds_client, args.train_dataset_ids, 'train')
    get_data(mds_client, args.test_dataset_ids, 'test')
    get_data(mds_client, args.online_dataset_ids, 'online')


if __name__ == '__main__':
    args = parse_args()
    main(args)
