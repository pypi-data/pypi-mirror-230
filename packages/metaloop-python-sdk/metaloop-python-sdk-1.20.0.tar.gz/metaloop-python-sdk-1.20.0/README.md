# Python SDK for Metaloop platform
Metaloop Python SDK is a python library to access [Metaloop](http://data.deepglint.com/)
and manage your datasets.
It provides:

-   A pythonic way to access your Metaloop resources by Metaloop OpenAPI [api](http://data.deepglint.com/api/v1/docs/).


## Installation

```console
pip install metaloop-python-sdk
```

## Documentation

More information can be found on the [examples](https://gitlab.deepglint.com/metaloop/metaloop-python-sdk/-/tree/dev/metaloop/examples)

## Usage
生成API Token
```
  在登录平台后，点击页面右上角的用户名，在个人信息页面中，即可获取本用户的API Token
  正式环境将http://192.168.100.71:30301 替换为 http://data.deepglint.com
```
操作数据集
```python
import time

from metaloop.client import MDS


if __name__ == '__main__':
    # use MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.71:30301") when connecting test-server
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0")

    date_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dataset_name = f"test_dataset_{date_time}"

    # create new dataset
    dataset = mds_client.create_dataset(
        dataset_name,
        "image",
        ["screw"],
        comment="this is a test dataset for mds"
    )
    # print dataset info
    dataset.summary()
    
    # get existed dataset
    dataset = mds_client.get_dataset(dataset_name)
    dataset.summary()

    # create version
    dataset.create_version(comment="this is a test version for mds")
    dataset.summary()

    # switch version
    dataset.checkout(0)
    dataset.summary()
    
    # import local data to dataset
    dataset.import_data("import_test/sample_test")
    # accelerated when running on tencent cloud
    dataset.import_data("import_test/sample_test", storage_type='cos')
    # export data to local filesystem
    dataset.export_data("export_test")
    # delete version
    dataset.delete_version(0)
    dataset.summary()
    # iter objects
    for item in dataset:
        print(item)
        response = requests.get(item['obj_url'])
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.show()
    # delete dataset
    mds_client.delete_dataset(dataset_name)
    dataset.summary()
        
```

## Development
- CI pipeline
