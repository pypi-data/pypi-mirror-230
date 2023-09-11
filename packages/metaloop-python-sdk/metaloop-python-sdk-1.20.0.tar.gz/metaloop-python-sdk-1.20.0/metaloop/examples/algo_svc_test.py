from metaloop.client import MDS

if __name__ == '__main__':
    client = MDS("da9c0bab-334f-41c1-9d28-dcc5806fe686", "http://192.168.100.115:30301")
    resp = client.update_algo_svc_test(id=1, status=MDS.ALGOSVCTEST.SUCCESS)
    print(resp)
