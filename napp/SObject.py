import cv2
import numpy as np
import json 

class SObject():

	def __init__(self, config):

		self.semLabel = config['semLabel']
		self.position = config['position']
		self.id = config['id']

	def Dump(self):

		objCfg = {
		  "semLabel": self.semLabel,
		  "position": self.position,
		  "id": self.id
		}

		return objCfg
