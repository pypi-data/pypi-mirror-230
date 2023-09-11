from metaloop.client import MDS

if __name__ == '__main__':
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.71:30301")
    resp = mds_client.send_notice("test_notice", MDS.NOTICE.SUCCEED, "这是一条测试通知的信息")
    print(resp)

