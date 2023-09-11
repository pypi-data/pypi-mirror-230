"""Client for communicating with the echo server"""
import socketio
import os
import uuid

from . import camera

class bcolors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'

ID = str(uuid.uuid1())[:8]

sio = socketio.Client()
@sio.event
def connect():
	print("(URN) connected to server")
	change_id(ID)

@sio.event
def disconnect():
    print("(URN) disconnected from server")

@sio.on('log')
def message(data):
	print('(Renderer) ' + data)

@sio.on('log-warning')
def message(data):
	print('(Renderer) ' + bcolors.WARNING + data)

@sio.on('log-error')
def message(data):
	print('(Renderer) ' + bcolors.FAIL + data)

@sio.on('ReceiveCameraImgMeta')
def receive_camera_img_meta(data):
	camera.receive_camera_img_meta(data)
	
@sio.on('ReceiveCameraImg')
def receive_camera_img(data):
  camera.receive_camera_img(data)
def connected():
	return sio.connected

def close():
	"""Disconnect from the echo server
	"""
	sio.disconnect()

def change_id(newID):
	"""Change the ID used to connect to the echo server

	Parameters
	----------
	newID : string
		New ID to connect with
	"""
	sio.emit('ID',[newID,"send"])
	print(f'Login sent with ID: {newID}, copy this ID into the renderer to connect.')