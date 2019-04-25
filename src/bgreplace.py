import cv2
import numpy as np

from object_detect import sdd_od
#from OpenPose import OpenPoseImage

def replace(img_path = '', bgimg_path = '', bg_color='', user_mask = None):

	if img_path == '':
		return None
	if bgimg_path == '' and bg_color == '':
		return None
	
	image = cv2.imread(img_path)
	(h, w) = image.shape[:2]

	
	#find bounding rectangle
	rect = (10,10,w-10,h-10)
	#rect = (150,55,620,1151)
	bounds = sdd_od.bounding_rect(image, prototxt = 'src/object_detect/MobileNetSSD_deploy.prototxt.txt', model = 'src/object_detect/MobileNetSSD_deploy.caffemodel')
	if bounds != None:
	    rect = (bounds[0]-20, 10, bounds[2]-bounds[0]+50, h-10)
	

	#grabcut
	img = image.copy()
	(h, w) = img.shape[:2]

	mask2 = np.zeros(img.shape[:2],np.uint8)

	bgdModel = np.zeros((1,65),np.float64)
	fgdModel = np.zeros((1,65),np.float64)

	cv2.grabCut(img,mask2,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)

	mask2 = np.where((mask2==2)|(mask2==0),cv2.GC_PR_BGD,1).astype('uint8')
	mask2[np.where((mask2 == 1)|(mask2 == 3))] = cv2.GC_PR_FGD
	#img = img*mask2[:,:,np.newaxis]
	#mask2[:,:] = cv2.GC_PR_BGD
	#mask2[h:h-10,rect[0]:rect[2]-rect[0]] = cv2.GC_PR_FGD


	#detect face -> hair
	face_cascade = cv2.CascadeClassifier('src/face_detect/haarcascade_frontalface_alt.xml')
	#img = image[10:h-10,bounds[0]:bounds[2]]
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)

	if len(faces) != 0:
		for (rx, ry, rw, rh) in faces:
			#cv2.rectangle(mask2, (int(rx+0.4*rw), ry-12), (int(rx+0.6*rw), ry-10), 255, -1)
			cv2.rectangle(mask2, (rx,ry), (rx+rw,ry+rh), cv2.GC_FGD, -1)
		#mask2[mask2 == 255] = cv2.GC_PR_FGD
		#mask2[mask2 == 0] = cv2.GC_PR_BGD
	else:
		#mask = np.zeros(img.shape[:2],np.uint8)
		pass

	#mask2[np.where((OpenPoseImage.pose_detect(image) == [255,0,0]).all(axis = 2))] = cv2.GC_FGD

	if user_mask != None:
		temp1 = cv2.inRange(user_mask, np.array([0, 0, 230], dtype = "uint8"), np.array([10, 10, 255], dtype = "uint8"))
		temp2 = cv2.inRange(user_mask, np.array([230, 0, 0], dtype = "uint8"), np.array([255, 10, 10], dtype = "uint8"))

		mask2[temp1 != 0] = cv2.GC_BGD
		mask2[temp2 != 0] = cv2.GC_FGD

	bgdModel = np.zeros((1,65),np.float64)
	fgdModel = np.zeros((1,65),np.float64)

	mask, bgdModel, fgdModel = cv2.grabCut(image,mask2,None,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_MASK)
	mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
	img = image*mask[:,:,np.newaxis]

	#combine backgrounds
	#imgnew = img.copy()
	#imgnew[np.where((imgnew != [0,0,0]).all(axis = 2) & (fg_masked == [0,0,0]).all(axis = 2))] = [0,0,0]

	#replace background
	
	if bgimg_path != '':
		bgimg = cv2.imread(bgimg_path)
		(h1, w1) = bgimg.shape[:2]

		#bgimg = bgimg[int(h1/2 - h/2) : int(h1/2 + h/2), int(w1/2 - w/2) : int(w1/2 + w/2)]
		bgimg = cv2.resize(bgimg,(w,h))
		bgimg[np.where((mask[:,:,np.newaxis] != 0).all(axis = 2))] = [0,0,0]

		#cv2.imshow('image',cv2.resize(bgimg+img,(300,400)))
		#cv2.waitKey(0)	

		return bgimg+img

	else:
		#hex to bgr
		bg_color = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))[::-1]

		img[np.where((img == [0,0,0]).all(axis = 2))] = bg_color

		return img
	

#replace()