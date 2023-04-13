import cv2
import time
from static import Static
from static import *
from common import emit_status_camera
from threading import Thread

def streamming_in_background(socketio):
    start = time.time()
    fps = 3
    duration = 1 / fps
    while True:
        if not Static.isStream:
            break
        end = time.time()
        if end - start < duration or Static.frame_stream is None:
            time.sleep(0.01)
            continue
        frame_stream = cv2.resize(Static.frame_stream, Static.resolution_stream)
        byteimg = cv2.imencode('.jpg', frame_stream)[1].tobytes()
        socketio.emit("frame", byteimg)
        start = end

def run_in_background(socketio):
    while True:
        if Static.stop or Static.camid == None:
            time.sleep(0.5)
            Static.status_camera = False
            continue
        source = cv2.VideoCapture(int(Static.camid), cv2.CAP_DSHOW)
        source.set(cv2.CAP_PROP_FRAME_WIDTH, Static.resolution[0])
        source.set(cv2.CAP_PROP_FRAME_HEIGHT, Static.resolution[1])
        source.set(cv2.CAP_PROP_EXPOSURE, Static.exposure)
        
        if not source.isOpened():
            time.sleep(0.5)
            Static.status_camera = False
            continue
        Static.status_camera = True
        while True:
           
           if Static.isChangeResolution == CHANGE_RESOLUTION:
               Static.isChangeResolution = EMIT_CHANGE_EXPOSURE
               source.set(cv2.CAP_PROP_FRAME_WIDTH, Static.resolution[0])
               source.set(cv2.CAP_PROP_FRAME_HEIGHT, Static.resolution[1])
               source.set(cv2.CAP_PROP_EXPOSURE, Static.exposure)
               continue
           
           isFrame, Static.frame = source.read()
           
           if not isFrame or Static.stop:
               Static.status_camera = False
               source.release()
               break
           
           if Static.isChangeResolution == EMIT_CHANGE_EXPOSURE:
               emit_status_camera(socketio, 1)
               Static.isChangeResolution = NONE_ACTION
               
           Static.frame_stream = Static.frame.copy()
        source.release()
        time.sleep(0.01)
