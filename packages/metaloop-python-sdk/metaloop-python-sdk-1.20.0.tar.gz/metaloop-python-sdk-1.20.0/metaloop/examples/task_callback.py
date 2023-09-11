import time

from metaloop.client import MDS


if __name__ == '__main__':
    mds_client = MDS("0c02ca70e142b75a75ca4118ce33dbb0", "http://192.168.100.38:30301")
    resp = mds_client.x_api.callback_task('1',{
        'status':'finished',
        'data':{
            'points':[{'name':'CLIP-RN','x':21,'y':0.86}]
        }
    })
    print(resp)

