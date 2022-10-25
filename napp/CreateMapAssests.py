import cv2
import numpy as np
from matplotlib import pyplot as plt
import random as rng
import yaml
import json
import os
from Room import Room

def SegmentRoom(img, folderPath, roomsegName, roomnum):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)

	# # noise removal
	kernel = np.ones((5,5),np.uint8)
	opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
	erosion_size = 3
	element = cv2.getStructuringElement( cv2.MORPH_RECT, ( 2*erosion_size + 1, 2*erosion_size+1 ), ( erosion_size, erosion_size ) );

	morph_res = thresh
	erosion_cnt = 0
	uniq_label_cnt = 0

	while(uniq_label_cnt != roomnum +1):
		morph_res = cv2.erode( morph_res, element )
		# cv2.imshow( "morph_res", morph_res );
		# cv2.waitKey()
		erosion_cnt += 1
		ret, labels =  cv2.connectedComponents(	morph_res) 
		uniq_label_cnt = len(np.unique(labels))
		print(uniq_label_cnt)

	while(erosion_cnt):
		morph_res = cv2.dilate( morph_res, element )
		erosion_cnt -= 1


	contours, hierarchy = cv2.findContours(morph_res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	#roomseg = 255 * np.ones(morph_res.shape).astype("uint8")
	roomseg = np.zeros(morph_res.shape).astype("uint8")
	roomids = np.arange(1, len(contours) + 1)
	rng.seed(12345)
	rid = 0

	for cnt in contours:
		mask = np.zeros(morph_res.shape).astype("uint8")
		x,y,w,h = cv2.boundingRect(cnt)
		cv2.rectangle(mask,(x,y),(x+w,y+h),255,-1)
		color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
		img[mask > 0 ] = color 
		roomseg[mask > 0 ] = roomids[rid]
		rid += 1

	cv2.imwrite(folderPath + roomsegName, roomseg)	



def extractObject(roomSeg, roomID, objectMap):

	ind = np.where(roomSeg == roomID + 1)	
	print

	objects = []
	ret, thresh = cv2.threshold(objectMap, 127, 255, 0)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:

		pnts = []
		for p in cnt:
			pnts.append(p[0].tolist())


		pos = [pnts[0][0], pnts[0][1], pnts[2][0], pnts[2][1]]
		uvs = [[pnts[0][0], pnts[0][1]], [pnts[2][0], pnts[2][1]]]

		updateObj = False
		for uv in uvs:
			val = roomSeg[uv[1], uv[0]]
			if val == roomID + 1:
				updateObj = True

		if updateObj:
			objects.append(pos)


	return objects	



def createConfig(folderPath, yaml_data, roomsegName, roomnum, classes, categories):

	imageName = yaml_data['image']
	roomSeg = cv2.imread(folderPath + roomsegName, 0)

	origin = yaml_data['origin']
	resolution = yaml_data['resolution']
	roomCfgs = []
	rooms = []
	semMaps = []

	for i in range(roomnum):
		roomCfg = {
		  "name": str(i),
	      "purpose": 0,
	      "id": i,
	      "objects": []
		}
		room = Room(roomCfg)
		rooms.append(room)
		roomCfgs.append(roomCfg)

	if os.path.isdir(folderPath + "SemMaps/"):
		roomCfgs.clear()
		for c in classes:
			semMap = cv2.imread(folderPath + "SemMaps/" + c + ".png", 0)
			semMaps.append(semMap)

		for i in range(roomnum):
			room = rooms[i]
			objects = []

			for s in range(len(semMaps)):
				objects_bw = extractObject(roomSeg, i, semMaps[s])
				for o in objects_bw:
					room.AddObject(s, o)


			roomCfg = room.Dump()
			#print(roomCfg)
			roomCfgs.append(roomCfg)
		

	floorCfg = {
		
		"name": "0",
		"roomSeg": roomsegName,
		"map": [{
		    "type": "GMap",
		    "image": imageName,
		    "resolution": resolution,
		    "origin": origin,
		    "negate": 0,
		    "occupied_thresh": 0.65,
		    "free_thresh": 0.196,
		    "augment" : 0
		  }],
		"semantic": {
		     "classes": classes,
		     "categories" : categories
		  },
		  "rooms": roomCfgs
	}

	with open(folderPath + "floor.config", "wt") as fp:
				json.dump(floorCfg, fp, indent=2)


def main():

	yamlPath = "/home/nickybones/Code/Maphisto/data/JMap/JMap.yaml"
	roomnum = 19
	roomsegName = "roomseg.png"
	classes = ['sink', 'door', 'oven', 'whiteboard', 'table', 'cardboard', 'plant', 'drawers', 'sofa', 'storage', 'chair', 'extinguisher', 'people', 'desk']
	categories = ["office", "corridor", "kitchen", "reception"]

	with open(yamlPath, "r") as stream:
	    try:
	    	yaml_data = yaml.safe_load(stream)
	    except yaml.YAMLError as exc:
	        print(exc)

	folderPath = os.path.split(os.path.abspath(yamlPath))[0] + "/"

	img = cv2.imread(folderPath + yaml_data['image'])
	#SegmentRoom(img, folderPath, roomsegName, roomnum)
	createConfig(folderPath, yaml_data, roomsegName, roomnum, classes, categories)


if __name__ == '__main__':
	main()



# yamlPath = "/home/nickybones/Code/Maphisto/data/JMap/JMap.yaml"
# roomnum = 19
# roomsegName = "roomseg.png"
# classes = ['sink', 'door', 'oven', 'whiteboard', 'table', 'cardboard', 'plant', 'drawers', 'sofa', 'storage', 'chair', 'extinguisher', 'people', 'desk']

# with open(yamlPath, "r") as stream:
#     try:
#     	yaml_data = yaml.safe_load(stream)
#     except yaml.YAMLError as exc:
#         print(exc)

# folderPath = os.path.split(os.path.abspath(yamlPath))[0] + "/"
# imageName = yaml_data['image']
# origin = yaml_data['origin']
# resolution = yaml_data['resolution']

# img = cv2.imread(folderPath + imageName)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ret, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)

# # # noise removal
# kernel = np.ones((5,5),np.uint8)
# opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
# erosion_size = 3
# element = cv2.getStructuringElement( cv2.MORPH_RECT, ( 2*erosion_size + 1, 2*erosion_size+1 ), ( erosion_size, erosion_size ) );

# morph_res = thresh
# erosion_cnt = 0
# uniq_label_cnt = 0

# while(uniq_label_cnt != roomnum +1):
# 	morph_res = cv2.erode( morph_res, element )
# 	# cv2.imshow( "morph_res", morph_res );
# 	# cv2.waitKey()
# 	erosion_cnt += 1
# 	ret, labels =  cv2.connectedComponents(	morph_res) 
# 	uniq_label_cnt = len(np.unique(labels))
# 	print(uniq_label_cnt)

# while(erosion_cnt):
# 	morph_res = cv2.dilate( morph_res, element )
# 	erosion_cnt -= 1


# contours, hierarchy = cv2.findContours(morph_res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# #roomseg = 255 * np.ones(morph_res.shape).astype("uint8")
# roomseg = np.zeros(morph_res.shape).astype("uint8")
# roomids = np.arange(1, len(contours) + 1)
# rng.seed(12345)
# rid = 0

# for cnt in contours:
# 	mask = np.zeros(morph_res.shape).astype("uint8")
# 	x,y,w,h = cv2.boundingRect(cnt)
# 	cv2.rectangle(mask,(x,y),(x+w,y+h),255,-1)
# 	color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
# 	img[mask > 0 ] = color 
# 	roomseg[mask > 0 ] = roomids[rid]
# 	rid += 1

# cv2.imwrite(folderPath + roomsegName, roomseg)	
# #cv2.imshow( "contour Demo", img );
# #cv2.waitKey()

# roomCfgs = []

# for i in range(roomnum):
# 	roomCfg = {
# 	"name": str(i),
#       "purpose": "office",
#       "id": i,
#       "objects": []
# 	}
# 	roomCfgs.append(roomCfg)

# floorCfg = {
	
# 	"name": "0",
# 	"roomSeg": roomsegName,
# 	"map": {
# 	    "type": "GMap",
# 	    "image": imageName,
# 	    "resolution": resolution,
# 	    "origin": origin,
# 	    "negate": 0,
# 	    "occupied_thresh": 0.65,
# 	    "free_thresh": 0.196
# 	  },
# 	"semantic": {
# 	     "classes": classes
# 	  },
# 	  "rooms": roomCfgs
# }

# with open(folderPath + "floor.config", "wt") as fp:
# 			json.dump(floorCfg, fp, indent=2)

