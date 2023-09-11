import cv2
import math
import numpy as np
videoTsMap = {}

def _genVideoTsMap(video_path):
    cap = cv2.VideoCapture(video_path)
    tsList = []
    while(cap.isOpened()):
        frame_exists, curr_frame = cap.read()
        if frame_exists:
            ts = cap.get(cv2.CAP_PROP_POS_MSEC)
            if len(tsList) == 0 or ts > 0:
                tsList.append(ts/1000.0)
        else:
            break
    cap.release()
    videoTsMap[video_path] = np.asarray(tsList)

def _find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array)):
        return idx - 1
    if idx > 0 and math.fabs(value - array[idx-1]) < math.fabs(value - array[idx]):
        return idx - 1
    else:
        return idx 

def getFrameIdByTs(video_path, ts):
    if video_path not in videoTsMap:
        _genVideoTsMap(video_path)
    return _find_nearest(videoTsMap[video_path], ts) + 1