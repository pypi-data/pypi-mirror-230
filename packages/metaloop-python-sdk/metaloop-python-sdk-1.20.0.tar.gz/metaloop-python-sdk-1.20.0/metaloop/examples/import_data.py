import time

from metaloop.client import MDS

if __name__ == '__main__':
    mds_client = MDS("0c03ca70e142b75a75ca4118ce33ddd0")

    dataset_name = f"test_dataset_for_sdk"

    # create dataset
    dataset = mds_client.create_dataset(
        dataset_name,
        "image",
        ["test"],
        comment="this is a test dataset for mds"
    )

    # import zip file
    dataset.import_data("import_test/sample_test.zip")
    dataset.summary()

    # import directory
    dataset.import_data("import_test/sample_test")
    dataset.summary()

    # import directory and save data to external cloud storage
    dataset.import_data("import_test/sample_test", storage_type="cos")
    dataset.summary()

    # import with object ids
    object_ids = []
    for item in dataset:
        print(item)
        object_ids.append(item['id'])
    dataset.import_data_with('object_id', object_ids)
    dataset.summary()

    # create a new version and inherit data from a previous version
    dataset.create_version(0, "this is a inherited test version")
    dataset.summary()

    mds_client.delete_dataset(dataset_name)
