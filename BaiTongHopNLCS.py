import imutils
import numpy as np
import cv2
import pytesseract
from imutils.perspective import four_point_transform
import sys
if sys.version_info[0] >= 3:
    unicode = str

from tkinter import *
from PIL import ImageTk, Image
import tkinter.filedialog as filedialog
import os

root = Tk()
root.geometry("600x400")
root.resizable(width=True, height=True)
global panel
global panel2
global text
global bottomframe
global topframe

#lay duong dan file duoc chon
def openfn():
    filename = filedialog.askopenfilename(parent=root,title='open')
    return filename

#xu ly
def process(imgPath):
	global panel2
	#doc hinh
	img = cv2.imread(imgPath,1)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray,(5,5),0)
	edged = cv2.Canny(blur,75,200)

	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts,key=cv2.contourArea,reverse=True)

	peri = cv2.arcLength(cnts[0],True)
	approx = cv2.approxPolyDP(cnts[0],0.02 * peri, True)

	idc1 = four_point_transform(img,approx.reshape(4,2))
	akt = cv2.resize(idc1,(794,499))
	cv2.imwrite('idc.jpg',akt)
	idc=cv2.imread('idc.jpg',1)

	img = cv2.multiply(idc, 1.1)
	kernel = np.ones((1, 1), np.uint8)
	img = cv2.erode(img, kernel, iterations=1)
	kernel1 = np.zeros( (5,7), np.float32)
	kernel1[3,3] = 3.2
	boxFilter = np.ones( (5,7), np.float32) / 90.0
	kernel1 = kernel1 - boxFilter
	img = cv2.filter2D(img, -1, kernel1)
	#cv2.imshow("img",img)


	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	h = float(gray.shape[0])

	maxVal = 255
	blockSize = 11
	C = 12.0*(90.0/h)

	bw = cv2.adaptiveThreshold(gray, maxVal, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, blockSize, C)
	#cv2.imshow('Binary Image', bw)

	bw = ~bw
	vertical = bw.copy()
	verticalsize = 4
	verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
	#cv2.imshow('Vertical Image', verticalStructure)


	#lam xoi mon hinh
	vertical = cv2.erode(vertical,kernel,iterations = 1)
	#cv2.imshow('',vertical)

	#lam mo nen
	vertical =cv2.morphologyEx(vertical, cv2.MORPH_CLOSE, kernel)
	#cv2.imshow('',vertical)

	vertical = cv2.dilate(vertical,kernel,iterations = 1)
	#cv2.imshow('',vertical)


	opening = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, kernel)

	cv2.imwrite('vertical.jpg',opening)
	
	global topframe
	
	#open hinh da xu ly
	img = Image.open("vertical.jpg")
	img = img.resize((250, 200),Image.ANTIALIAS)
	img = ImageTk.PhotoImage(img)
	#gan hinh vao top frame
	panel2 = Label(topframe, image=img)
	panel2.image = img
	panel2.pack(side="right")
	
	#cat tung khung thong tin
	cmnd_crop = vertical[115:170, 387:600]
	FNameT_crop = vertical[165:220, 330:750]
	Birth_crop = vertical[270:315, 370:760]
	NquanT_crop = vertical[310:360, 420:760]
	NquanD_crop = vertical[360:410, 230:760]
	DCT_crop = vertical[400:455, 495:765]
	DCD_crop = vertical[450:490, 230:765]
	
	#gan text thong tin vao bottom frame
	global bottomframe
	bottomframe = Frame(root)
	bottomframe.pack( side = "bottom" )
	global text
	text = Text(bottomframe)
	
	socm = pytesseract.image_to_string(cmnd_crop, lang='vie')
	text.insert('insert', "Số CM: ")
	text.insert('insert',socm)

	ten = pytesseract.image_to_string(FNameT_crop, lang='vie')
	text.insert('insert', "\nHọ tên: ")
	text.insert('insert',ten)

	sn = pytesseract.image_to_string(Birth_crop, lang='vie')
	text.insert('insert', "\nNgày sinh: ")
	text.insert('insert',sn)

	qq1 = pytesseract.image_to_string(NquanT_crop, lang='vie')
	qq2 = pytesseract.image_to_string(NquanD_crop, lang='vie')
	text.insert('insert', "\nQuê quán:")
	text.insert('insert',qq1)
	text.insert('insert', " ")
	text.insert('insert',qq2)

	dc1 = pytesseract.image_to_string(DCT_crop, lang='vie')
	dc2 = pytesseract.image_to_string(DCD_crop, lang='vie')
	text.insert('insert', "\nHKTT: ")
	text.insert('insert',dc1)
	text.insert('insert', " ")
	text.insert('insert',dc2)
	
	text.pack(side="bottom")

#reset root
def clear():
	global topframe
	global panel
	global panel2
	global text
	global bottomframe
	topframe.destroy()
	bottomframe.destroy()
	text.destroy()
	panel.destroy()
	panel2.destroy()
	
#open hinh duoc chon
def open_img():
	#gan hinh goc vao top frame
	global panel
	global topframe
	topframe = Frame(root)
	topframe.pack( side = "top" )
	
	path = openfn()
	img = Image.open(path)
	img = img.resize((250, 200), Image.ANTIALIAS)
	img = ImageTk.PhotoImage(img)
	
	panel = Label(topframe, image=img)
	panel.image = img
	panel.pack(side="left")
	process(path)


#nut open file
btn = Button(root, text='open image', command=open_img).pack()

#nut reset
btn = Button(root, text='Reset', command=clear).pack()

root.mainloop()
