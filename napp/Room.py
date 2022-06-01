import cv2
import numpy as np
import json 
from SObject import SObject
import random

class Room():

	def __init__(self, config):

		self.name = config['name']
		self.purpose = config['purpose']
		self.id = config['id']
		self.objects = []
		self.ids = []

		for objCfg in config['objects']:
			obj = SObject(objCfg)
			self.objects.append(obj)
			self.ids.append(obj.id)

	def CreateObject(self, semLabel=0, position=[0, 0, 0, 0]):

		oid = random.randint(0, 200)
		while oid in self.ids:
			oid = random.randint(0, 200)

		objCfg = {
		  "semLabel": semLabel,
		  "position": position,
		  "id": oid
		}

		obj = SObject(objCfg)
		return obj

	def AddObject(self, semLabel=0, position=[0, 0, 0, 0]):

		oid = random.randint(0, 200)
		while oid in self.ids:
			oid = random.randint(0, 200)

		objCfg = {
		  "semLabel": semLabel,
		  "position": position,
		  "id": oid
		}

		obj = SObject(objCfg)

		self.objects.append(obj)
		self.ids.append(obj.id)

	def RemoveObject(self, id):
		self.objects.pop(id)
		self.ids.pop(id)



	def Dump(self):

		objCfgs = []
		for i in range(len(self.objects)):
			obj = self.objects[i]
			objCfgs.append(obj.Dump())

		roomCfg = {
		  "name": self.name,
		  "purpose": self.purpose,
		  "id": self.id,
		  "objects" : objCfgs
		}

		return roomCfg