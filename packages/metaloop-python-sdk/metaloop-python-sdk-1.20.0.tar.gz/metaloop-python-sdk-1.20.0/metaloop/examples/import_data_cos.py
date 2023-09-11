import time

from metaloop.client import MDS

if __name__ == '__main__':
    mds_client = MDS("4057deac-6700-47d8-a4fc-a3c4854502a0", "http://192.168.100.71:30301")

    # get dataset
    dataset = mds_client.get_dataset("SDK测试使用")
    dataset.summary()

    dataset.import_data("import_test/sample_test", storage_type='cos')

    # export data to local
    dataset.export_data("export_test_cos")


