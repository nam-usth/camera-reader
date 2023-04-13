def emit_status_camera(socketio, status):
    socketio.emit("camera_ready", {"readyFlg" : status})
