import time

from metaloop.client import MDS

is_show = False
if is_show:
    from io import BytesIO
    import requests
    from PIL import Image

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

    # import directory
    dataset.import_data("import_test/sample_test.zip")

    for item in dataset:
        print(item)
        if is_show:
            response = requests.get(item['obj_url'])
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image.show()
    mds_client.delete_dataset(dataset_name)
