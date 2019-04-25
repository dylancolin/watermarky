import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ctypes
import warnings, sys, os

from src import bgreplace


warnings.filterwarnings("ignore")

myappid = 'finityss.nishees.watermarky.2.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

font_size = 11
font_style = "Comic Sans"

icon_path = "images/static/icon.png"
logo_path = "images/static/logo.png"
temp_path = ""
init_sel = "images/static/no_img.png"
init_prev = "images/static/no_prev.jpg"
watermarked_path = "images/watermarked/"


def add_watermark(sel_image, prod_id):
	#temp = np.ones((50, 150, 4), dtype="uint8") * 255
	temp = np.zeros((50,150,4), dtype="uint8")
	cv2.putText(temp, prod_id, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, lineType=8)
	(wH1, wW1) = temp.shape[:2]

	watermark = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
	(wH2, wW2) = watermark.shape[:2]
	#eliminating some strange issues of opencv
	(B, G, R, A) = cv2.split(watermark)
	B = cv2.bitwise_and(B, B, mask=A)
	G = cv2.bitwise_and(G, G, mask=A)
	R = cv2.bitwise_and(R, R, mask=A)
	watermark = cv2.merge([B, G, R, A])

	# load the input image, then add an extra dimension to the image (i.e., the alpha transparency)
	image = cv2.imread(sel_image)
	(h, w) = image.shape[:2]
	image = np.dstack([image, np.ones((h, w), dtype="uint8") * 255])

	#resize logo
	'''wsize = int(min(h, w) * 0.25)
	wpercent = (wsize / float(wH2))
	hsize = int((float(wW2) * float(wpercent)))
	watermark = cv2.resize(watermark, (wsize, hsize))
	(wH2, wW2) = watermark.shape[:2]'''

	# construct an overlay that is the same size as the input
	# image, (using an extra dimension for the alpha transparency),
	# then add the watermark to the overlay in the bottom-right corner
	overlay = np.zeros((h, w, 4), dtype="uint8")

	overlay[10:10 + wH2, 10:wW2 + 10] = watermark

	overlay[h - wH1 - 10:h - 10, 10:10 + wW1] = temp
	#cv2.putText(overlay, prod_id, (10, h-60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, lineType=8)

	# blend the two images together using transparent overlays
	output = image.copy()
	cv2.addWeighted(overlay, 0.8, output, 1.0, 0, output)

	cv2.imwrite(temp_path, output)

	#cv2.imshow('image',temp)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()


def add_logo(sel_image, mod_image, prod_id):
	#print sel_image
	if mod_image == None:
		image = cv2.imread(sel_image)
	else:
		image = mod_image

	(h, w) = image.shape[:2]
	image = np.dstack([image, np.ones((h, w), dtype="uint8") * 255])

	watermark = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
	(wH2, wW2) = watermark.shape[:2]
	#eliminating some strange issues of opencv
	(B, G, R, A) = cv2.split(watermark)
	B = cv2.bitwise_and(B, B, mask=A)
	G = cv2.bitwise_and(G, G, mask=A)
	R = cv2.bitwise_and(R, R, mask=A)
	watermark = cv2.merge([B, G, R, A])

	if min(h, w) == w:
		wsize = int(float(w) / float(3.45))
		hsize = int((float(w) / float(3.45) ) * (float(wH2) / float(wW2)))
	elif min(h,w) == h:
		wsize = int(float(h) / float(8.67))
		hsize = int((float(h) / float(8.67) ) * (float(wH2) / float(wW2)))	

	if w > h and w > 1000:
		wsize = 223
		hsize = 127

	watermark = cv2.resize(watermark, (wsize, hsize))
	(wH2, wW2) = watermark.shape[:2]

	'''wsize = int((float(w) / float(3.45)))
	hsize = int((float(h) / float(8.67)))
	watermark = cv2.resize(watermark, (wsize, hsize))
	(wH2, wW2) = watermark.shape[:2]'''

	alpha_s = watermark[:, :, 3] / 255.0
	alpha_l = 1.0 - alpha_s
	for c in range(0, 3):
		image[10:10 + wH2, 10:wW2 + 10, c] = (alpha_s * watermark[:, :, c] + alpha_l * image[10:10 + wH2, 10:wW2 + 10, c])

	'''temp = np.zeros((50,150,4), dtype="uint8")
	cv2.putText(temp, prod_id, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (41,41,142), 2, lineType=8)
	(wH1, wW1) = temp.shape[:2]

	alpha_s = temp[:, :, 3] / 255.0
	alpha_l = 1.0 - alpha_s
	for c in range(0, 3):
		image[h - wH1 - 10:h - 10, 10:10 + wW1, c] = (alpha_s * temp[:, :, c] + alpha_l * image[h - wH1 - 10:h - 10, 10:10 + wW1, c])'''

	#image[h - wH1 - 10:h - 10, 10:10 + wW1] = temp
	#500 -> 0.6	
	weight = 1 if min(h, w) < 500 else 2
	cv2.putText(image, prod_id, (10, h-60), cv2.FONT_HERSHEY_SIMPLEX, min(h, w) * 0.6 / 500, (41,41,142), weight, lineType=8)

	cv2.imwrite(temp_path, image)



class Window(QMainWindow):

	resized = pyqtSignal()

	def __init__(self, parent=None):
	    super(Window, self).__init__(parent=parent)
	    self.setGeometry(100, 50, 650, 640)
	    self.setWindowTitle("Watermarky")
	    self.setWindowIcon(QIcon(icon_path))
	    self.fname = ""
	    self.resized.connect(self.resize_update)
	    self.x1 = self.width() / 2 - 325
	    self.y1 = 0
	    self.__mousePressPos = None
	    self.__mouseMovePos = None
	    self.active_color = QColor(0,0,255,255)
	    self.home()

	def resizeEvent(self, event):
	    self.resized.emit()
	    return super(Window, self).resizeEvent(event)


	def mousePressEvent(self, event):
		posMouse =  event.pos()
		self.__mousePressPos = None
		self.__mouseMovePos = None
		if QRect(QPoint(self.x1+20, self.y1+140), QSize(300, 400)).contains(posMouse):
		    self.__mousePressPos = posMouse
		    self.__mouseMovePos = posMouse

		super(Window, self).mousePressEvent(event)

	def mouseMoveEvent(self, event):
		posMouse =  event.pos()
		#print "posmouse ",posMouse
		if QRect(QPoint(self.x1+20, self.y1+140), QSize(300, 400)).contains(posMouse) and self.__mousePressPos is not None:
			self.painter.begin(self.pixmap_sel)
			self.painter.setPen(QPen(self.active_color, 4))
			self.painter.drawLine(self.__mouseMovePos.x()-20-self.x1,self.__mouseMovePos.y()-140-self.y1,posMouse.x()-20-self.x1,posMouse.y()-140-self.y1)
			self.painter.end()
			self.sel_pic.setPixmap(self.pixmap_sel)
			self.sel_pic.repaint()
			self.__mouseMovePos = posMouse
		else:
			self.__mousePressPos = None
			self.__mouseMovePos = None

		super(Window, self).mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self.__mousePressPos = None
		self.__mouseMovePos = None

		super(Window, self).mouseReleaseEvent(event)


	def home(self):

	    self.logo_pic = QLabel(self)
	    pixmap = QPixmap(logo_path)
	    pixmap = pixmap.scaled(300, 100, Qt.KeepAspectRatio)
	    self.logo_pic.setPixmap(pixmap)
	    self.logo_pic.resize(300,100)
	    self.logo_pic.show()

	    self.prod_id_text = QLabel("PRODUCT ID", self)
	    self.prod_id_text.setFont(QFont(font_style,font_size))
	    self.prod_id_text.move(self.x1 + 340, self.y1 + 20)

	    self.prod_id = QLineEdit("", self)
	    self.prod_id.setFont(QFont(font_style,font_size))
	    self.prod_id.move(self.x1 + 440, self.y1 + 20)
	    self.prod_id.resize(160,40)

	    self.cb_select = QComboBox(self)
	    self.cb_select.addItems(["SELECT IMAGE","SELECT MULTIPLE"])
	    self.cb_select.move(self.x1 + 220, self.y1 + 101)
	    #self.cb.currentIndexChanged.connect(self.bg_choice)
	    self.cb_select.activated[str].connect(self.cb_selected)

	    self.sel_pic = QLabel(self)
	    self.pixmap_sel = QPixmap(init_sel)
	    self.pixmap_sel = self.pixmap_sel.scaled(300, 400, Qt.KeepAspectRatio)
	    self.painter = QPainter(self.pixmap_sel)
	    #self.painter.drawPixmap(self.sel_pic.rect(), self.pixmap_sel)
	    #self.painter.setPen(QPen(self.active_color, 3))
	    self.painter.end()	    
	    self.sel_pic.setPixmap(self.pixmap_sel)
	    self.sel_pic.move(self.x1 + 20, self.y1 + 140)
	    self.sel_pic.resize(300,400)	    
	    self.sel_pic.show()


	    self.cb = QComboBox(self)
	    self.cb.addItems(["SELECT BACKGROUND COLOR", "SELECT BACKGROUND IMAGE"])
	    self.cb.move(self.x1 + 340, self.y1 + 101)
	    self.cb.resize(200,25)		
	    #self.cb.currentIndexChanged.connect(self.bg_choice)
	    self.cb.activated[str].connect(self.bg_choice)


	    self.prev_text = QPushButton("PREVIEW "+u'\u2193', self)
	    self.prev_text.move(self.x1 + 560, self.y1 + 100)
	    self.prev_text.resize(70,25)
	    self.prev_text.clicked.connect(self.show_preview)

	    self.prev_pic = QLabel(self)
	    pixmap = QPixmap(init_prev)
	    pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
	    self.prev_pic.setPixmap(pixmap)
	    self.prev_pic.move(self.x1 + 340, self.y1 +140)
	    self.prev_pic.resize(300,400)
	    self.prev_pic.show()

	    self.white_btn = QPushButton("", self)
	    self.white_btn.setFont(QFont(font_style,font_size))
	    self.white_btn.setStyleSheet("background-color: blue; border:1px solid #000;")
	    self.white_btn.move(self.x1 + 20, self.y1 +550)	
	    self.white_btn.resize(20,20)
	    self.white_btn.clicked.connect(self.white_btn_clkd)

	    self.black_btn = QPushButton("", self)
	    self.black_btn.setFont(QFont(font_style,font_size))
	    self.black_btn.setStyleSheet("background-color: red; border:1px solid #000;")
	    self.black_btn.move(self.x1 + 50, self.y1 +550)	
	    self.black_btn.resize(20,20)
	    self.black_btn.clicked.connect(self.black_btn_clkd)

	    self.clear_btn = QPushButton("X", self)
	    self.clear_btn.setFont(QFont(font_style,font_size))
	    self.clear_btn.setStyleSheet("background:none; font-weight:bold;color:#8E2929")
	    self.clear_btn.move(self.x1 + 80, self.y1 +550)	
	    self.clear_btn.resize(20,20)
	    self.clear_btn.clicked.connect(self.clear_btn_clkd)

	    self.done_btn = QPushButton("DONE", self)
	    self.done_btn.setFont(QFont(font_style,font_size))
	    self.done_btn.move(self.x1 + 340, self.y1 +550)	
	    self.done_btn.resize(300,30)
	    self.done_btn.clicked.connect(lambda:done_btn_clkd(self))

	    self.copyright = QLabel(self)
	    self.copyright.setText('''Copyrights 2018. All rights reserved. Desgned & Developed By <a href='http://finitysoftwaresolutions.com/'>Finity Software Solutions</a>''')
	    self.copyright.move(self.x1 + 115, self.y1 +600)
	    self.copyright.resize(450,40)

	    self.show()


	def resize_update(self):
	    self.x1 = self.width() / 2 - 325
	    self.y1 = 0

	    self.logo_pic.move(self.x1 + 20, self.y1 +0)
	    self.prod_id_text.move(self.x1 + 340, self.y1 + 20)	
	    self.prod_id.move(self.x1 + 440, self.y1 + 20)
	    self.cb_select.move(self.x1 + 220, self.y1 +100)
	    self.sel_pic.move(self.x1 + 20, self.y1 + 140)
	    self.prev_text.move(self.x1 + 560, self.y1 + 100)
	    self.cb.move(self.x1 + 340, self.y1 + 101)
	    self.prev_pic.move(self.x1 + 340, self.y1 +140)
	    self.white_btn.move(self.x1 + 20, self.y1 +550)	
	    self.black_btn.move(self.x1 + 50, self.y1 +550)	
	    self.clear_btn.move(self.x1 + 80, self.y1 +550)	
	    self.done_btn.move(self.x1 + 340, self.y1 +550)	
	    self.copyright.move(self.x1 + 115, self.y1 +600)

	
	def white_btn_clkd(self):
		self.active_color = QColor(0,0,255,255)

	def black_btn_clkd(self):
		self.active_color = QColor(255,0,0,255)
		
	def clear_btn_clkd(self):
		if str(self.fname) != "":
			self.pixmap_sel = QPixmap(self.fname)
			self.pixmap_sel = self.pixmap_sel.scaled(300, 400, Qt.KeepAspectRatio)
			self.sel_pic.setPixmap(self.pixmap_sel)
		else:
			self.pixmap_sel = QPixmap(init_sel)
			self.pixmap_sel = self.pixmap_sel.scaled(300, 400, Qt.KeepAspectRatio)
			self.sel_pic.setPixmap(self.pixmap_sel)		


	def get_mask_edited(self, sel_image):
		image = cv2.imread(sel_image)
		(h, w) = image.shape[:2]

		temp_path_pixmap1 = watermarked_path + 'edited_temp1.' +  str(sel_image).split("/")[-1].split(".")[-1]

		temp = self.pixmap_sel
		temp.scaled(w,h).save(temp_path_pixmap1)
			
		img1 = cv2.imread(temp_path_pixmap1)

		os.remove(temp_path_pixmap1)

		return img1


	def cb_selected(self, text):
		if text == "SELECT IMAGE":
			self.upload_csv()
		elif text == "SELECT MULTIPLE":
			self.folder_selected()


	def bg_choice(self, text):
		if text == "SELECT BACKGROUND COLOR":
			self.bgcolor_selected()
		elif text == "SELECT BACKGROUND IMAGE":
			self.bgimage_selected()


	def bgcolor_selected(self):
		color = QColorDialog.getColor()
		global temp_path
		if str(color.name()) == '#000000':
			pass
		else:
			if str(self.fname) == "":
				QMessageBox.warning(self, "Alert", "PLEASE SELECT A FILE")
			else:
				if str(self.prod_id.text()) == "":
					QMessageBox.warning(self, "Alert", "PLEASE ENTER A PRODUCT ID NUMBER")
				else:
					temp_path = watermarked_path + 'temp.' +  str(self.fname).split("/")[-1].split(".")[-1]

					bg_replaced = bgreplace.replace(img_path = str(self.fname), bgimg_path = '', bg_color=str(color.name()), 
						user_mask = self.get_mask_edited(sel_image= str(self.fname)))

					add_logo(sel_image= None, mod_image= bg_replaced, prod_id= str(self.prod_id.text()))

					pixmap = QPixmap(temp_path)
					pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
					self.prev_pic.setPixmap(pixmap)   	


	def bgimage_selected(self):
		dialog = QFileDialog()
		fname = dialog.getOpenFileName(None, "Import Image", "", "BACKGROUND Image File (*.jpg;*.jpeg;*.png)")  
		global temp_path

		if str(fname) == "":
			pass
		else:
			if str(self.fname) == "":
				QMessageBox.warning(self, "Alert", "PLEASE SELECT A FILE")
			else:
				if str(self.prod_id.text()) == "":
					QMessageBox.warning(self, "Alert", "PLEASE ENTER A PRODUCT ID NUMBER")
				else:
					temp_path = watermarked_path + 'temp.' +  str(self.fname).split("/")[-1].split(".")[-1]

					bg_replaced = bgreplace.replace(img_path = str(self.fname), bgimg_path = str(fname), bg_color='', 
						user_mask = self.get_mask_edited(sel_image= str(self.fname)))

					add_logo(sel_image= None, mod_image= bg_replaced, prod_id= str(self.prod_id.text()))

					pixmap = QPixmap(temp_path)
					pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
					self.prev_pic.setPixmap(pixmap)   



	def upload_csv(self):
		global temp_path

		dialog = QFileDialog()
		fname = dialog.getOpenFileName(None, "Import Image", "", "Product Image File (*.jpg;*.jpeg;*.png)")      

		if str(fname) == "":
			pass
		else:
			self.fname = fname

			self.pixmap_sel = QPixmap(self.fname)
			self.pixmap_sel = self.pixmap_sel.scaled(300, 400, Qt.KeepAspectRatio)
			self.sel_pic.setPixmap(self.pixmap_sel)

			if str(self.prod_id.text()) == "":
				temp_path = init_prev
			else:
				temp_path = watermarked_path + 'temp.' +  str(self.fname).split("/")[-1].split(".")[-1]
				add_logo(sel_image= str(self.fname), mod_image= None, prod_id= str(self.prod_id.text()))

			pixmap = QPixmap(temp_path)
			pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
			self.prev_pic.setPixmap(pixmap)


	def folder_selected(self):
		global temp_path

		files = QFileDialog.getOpenFileNames(None, "Import Images", "", "Product Image Files (*.jpg;*.jpeg;*.png)") 

		if len(files) != 0:
			for file in files:
				if os.path.splitext(str(file))[1] in {'.jpg','.jpeg','.png'}:

					temp_path = watermarked_path +  str(file).split("\\")[-1]
					add_logo(sel_image= (str(file)), mod_image= None, prod_id= os.path.splitext(str(file))[0].split("\\")[-1])

			QMessageBox.information(self, "Success", "Watermark added successfully to images in selected folder!")
		

	def show_preview(self):
		global temp_path
		if str(self.fname) == "":
			QMessageBox.warning(self, "Alert", "PLEASE SELECT A FILE")
		else:
			if str(self.prod_id.text()) == "":
				QMessageBox.warning(self, "Alert", "PLEASE ENTER A PRODUCT ID NUMBER")
			else:
				temp_path = watermarked_path + 'temp.' +  str(self.fname).split("/")[-1].split(".")[-1]
				#self.get_mask_edited(sel_image= str(self.fname))
				add_logo(sel_image= str(self.fname), mod_image= None, prod_id= str(self.prod_id.text()))

				pixmap = QPixmap(temp_path)
				pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
				self.prev_pic.setPixmap(pixmap)   		   
	


def done_btn_clkd(self):
	if str(self.fname) == "":
		QMessageBox.warning(self, "Alert", "No file selected")
	elif temp_path == init_prev or not os.path.isfile(temp_path):
		QMessageBox.warning(self, "Alert", "Cannot find the file. Please try again.")
	else:
		temp = cv2.imread(temp_path, cv2.IMREAD_UNCHANGED)
		os.remove(temp_path)
		cv2.imwrite(watermarked_path + str(self.fname).split("/")[-1], temp)

		self.prod_id.setText("")
		self.fname = ""

		self.pixmap_sel = QPixmap(init_sel)
		self.pixmap_sel = self.pixmap_sel.scaled(300, 400, Qt.KeepAspectRatio)
		self.sel_pic.setPixmap(self.pixmap_sel)

		pixmap = QPixmap(init_prev)
		pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
		self.prev_pic.setPixmap(pixmap)  

		QMessageBox.information(self, "Success", "Watermark added successfully !")



def main(args):

	if not os.path.exists(watermarked_path):
		os.makedirs(watermarked_path)

	app = QApplication(args)
	GUI = Window()

	sys.exit(app.exec_())



if __name__=="__main__":
    main(sys.argv)