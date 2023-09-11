import time

from metaloop.client import MDS


if __name__ == '__main__':
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.71:30301")

    date_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dataset_name = f"test_dataset_{date_time}"

    # create dataset
    dataset = mds_client.create_dataset(
        dataset_name,
        "image",
        ["screw"],
        comment="this is a test dataset for mds"
    )
    dataset.summary()

    # create version
    dataset.create_version(comment="this is a test version for mds")
    dataset.summary()

    # switch version
    dataset.checkout(0)
    dataset.summary()

    # delete version
    dataset.delete_version(0)
    dataset.summary()

    # delete dataset
    mds_client.delete_dataset(dataset_name)
    dataset.summary()
