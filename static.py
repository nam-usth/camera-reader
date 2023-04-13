import os

NONE_ACTION = 1
CHANGE_RESOLUTION = 2
STOP_CAPTURE = 3
CHANGE_EXPOSURE = 4
EMIT_CHANGE_EXPOSURE = 5

class Static:
    frame = None
    stop = False
    camid = None
    status_camera = False
    isStream = False
    resolution_stream = (256, 192)
    isChangeResolution = 1
    resolution = (640, 480)
    frame_stream = None
    exposure = -4