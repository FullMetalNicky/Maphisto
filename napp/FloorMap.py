import cv2
import numpy as np
import json 
from Room import Room
import os 

class FloorMap():

	def __init__(self, jsonPath):

		f = open(jsonPath)
		config = json.load(f)

		self.data_folder = os.path.split(os.path.abspath(jsonPath))[0] + "/"
		self.roomSeg = cv2.imread(self.data_folder + config['roomSeg'], 0)
		self.map = cv2.imread(self.data_folder + config['map']['image'])
		self.classes = config['semantic']['classes']
		self.rooms = []

		if 'rooms' in config:
			for roomCfg in config['rooms']:
				room = Room(roomCfg)
				self.rooms.append(room)



	def Dump(self, jsonPath):

		f = open(jsonPath)
		config = json.load(f)
		f.close()

		roomCfgs = []
		for i in range(len(self.rooms)):
			room = self.rooms[i]
			roomCfgs.append(room.Dump())

		config['rooms'] = roomCfgs

		with open(jsonPath, "wt") as fp:
			json.dump(config, fp, indent=2)
		