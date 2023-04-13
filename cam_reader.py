# 20/3/2023 20:55 PM

import cv2
from flask import Flask, request, jsonify, Response

from threading import Thread

#from gevent.pywsgi import WSGIServer
import time
from datetime import datetime
from flask import make_response
from flask_socketio import SocketIO
from static import Static
from static import *
from threads import streamming_in_background, run_in_background

# %% Application setting

app = Flask(__name__)
                
app.secret_key = 'You Will Never Guess'

socketio = SocketIO(app, logger=False, cors_allowed_origins='*')
socketio.init_app(app, cors_allowed_origins="*")

@socketio.on('connect')
def test_connect():
    print("client connect")

@socketio.on('disconnect')
def test_disconnect():
    Static.isStream = False
    print("client disconnect")

@socketio.on("start_stream")
def start_stream(_):
    if Static.isStream:
        socketio.emit("start_stream_status", {"status" : -1})
        return
    Static.isStream = True
    Thread(target=streamming_in_background, args=(socketio,)).start()
    socketio.emit("start_stream_status", {"status" : 1})

@socketio.on("stop_stream")
def stop_stream(_):
    Static.isStream = False
    socketio.emit("stop_stream_status", {"status" : 1})
    
@socketio.on("change_camera_settings")
def change_resolution(data):
    if 'resolution_width' in data.keys() and int(data["resolution_width"]) != 0 \
        and 'resolution_height' in data.keys() and int(data['resolution_height']) != 0: 
        width = int(data["resolution_width"])
        height = int(data['resolution_height'])
        Static.resolution = (width, height)
        Static.isChangeResolution = CHANGE_RESOLUTION
    if 'exposure' in data.keys():
        Static.exposure = int(data['exposure'])
        Static.isChangeResolution = CHANGE_RESOLUTION
    
@app.route('/frame', methods=['GET'])
def get_frame():
    if Static.frame is None:
        response = make_response(b'')
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='s.jpg')
        return response
    byteimg = cv2.imencode('.jpg', Static.frame)[1].tobytes()
    Static.frame = None
    response = make_response(byteimg)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set(
        'Content-Disposition', 'attachment', filename='s.jpg')
    return response

@app.route('/stop', methods=['GET'])
def stop_cam():
    Static.isStream = False
    Static.stop = True
    time_wait = 20
    status = None
    Static.camid = None
    
    f = open("camera_time_measure.txt", "a+")
    f.write("TURN OFF - Start " + str(Static.status_camera) + " - " + str(datetime.now()) + "\n")
    f.close() 
    
    while True:
        if not Static.status_camera:
            status = True
            break
        time.sleep(0.1)
        time_wait -= 1
        if time_wait <= 0:
            break
        
    f = open("camera_time_measure.txt", "a+")
    f.write("TURN OFF - End " + str(Static.status_camera) + " - " + str(datetime.now()) + "\n")
    f.close()
    
    return jsonify({
            "status" : 1 if status else -1
        })

@app.route("/camera_status/<camid_>", methods=["GET"])
def camera_status(camid_):
    if Static.camid != int(camid_):
        return jsonify({
            "status" : -1
            })
    return jsonify({
        "status" : 1 if Static.status_camera else -1
        })

@app.route('/start/<camid_>', methods=['GET'])
def start_cam(camid_):
    f = open("camera_time_measure.txt", "a+")
    f.write("TURN ON - Start " + str(Static.status_camera) + " - " + str(datetime.now()) + "\n")
    f.close()  
    
    if Static.status_camera:
        if Static.camid == int(camid_):
            return jsonify({
                "status" : -1,
                "mess" : f"Camera {Static.camid} is running"
                })
        else:
            return jsonify({
                "status" : -1,
                "mess" : f"Camera {Static.camid} is running. You must turn off before run cam {camid_}"
                })
    
    Static.stop = False
    Static.camid = int(camid_)
    time_wait = 100
    
    status = None
    while True:
        if Static.status_camera:
            status = True
            break
        time.sleep(0.1)
        time_wait -= 1
        if time_wait <= 0:
            break
        
    f = open("camera_time_measure.txt", "a+")
    f.write("TURN ON - End " + str(Static.status_camera) + " - " + str(datetime.now()) + "\n")
    f.close()    
        
    return jsonify({
            "status" : 1 if status else -1
        })

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({
        "img" : "hello"
        })

# %% Main function
if __name__ == '__main__':
    # Convert all JSON keys format to snake_case
    t = Thread(target=run_in_background, args=(socketio,))
    t.start()
    print("start server at port : ", 3000)
    socketio.run(app, host='127.0.0.1', port=3000)