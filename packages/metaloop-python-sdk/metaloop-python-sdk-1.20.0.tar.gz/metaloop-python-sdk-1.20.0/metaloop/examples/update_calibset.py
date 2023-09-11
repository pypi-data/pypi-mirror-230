from metaloop.client import MDS

if __name__ == '__main__':
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.115:30301")
    resp = mds_client.update_calibset(id=123, status=MDS.CALIB.PROCESSING, pb_url="/t", log="l1",
                                      folders="15", category=MDS.CALIB.DEFAULTCATEGORY)
    print(resp)