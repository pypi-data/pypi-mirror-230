from typing import Dict
from metaloop.client import MDS

if __name__ == '__main__':
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.71:30301")
    mc: Dict[str, any] = {
                "mpid": 6985,
                "enc_way": "NetWork",
                "minio_path": "minio_path",
                "ftp_path": "ftp_path",
                "secret_key": "secret_key",
                "status": 1,
                "is_arm": False
    }
    res = mds_client.call_model_convert_path_status(mc)
    print(res['code'] == 200)

    mtStatus: Dict[str, any] = {
        "mtid":  6985,
        "result_path": "测试结果路径",
        "eval_content": "模型测试eval内容",
        "perform_content": "模型测试perform内容",
        "status": 4
    }
    res = mds_client.call_model_test_status(mtStatus)
    print(res['code'] == 200)

    mtRes: Dict[str, any] = {
        "tid": 6985,
        "content": "content_111",
    }
    res = mds_client.call_model_test_result_content(mtRes)
    print(res['code'] == 200)

    res = mds_client.get_ppf_url_by_category("acl2101_x86")
    print(res)

