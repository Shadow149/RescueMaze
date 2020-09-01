"""
Example OpenCV letter detection
Written by Fatemeh Pahlevan Aghababa, Amirreza Kabiri, MohammadHossein Goharinejad - 2020

"""
import cv2
import numpy
import matplotlib.pyplot as plt



def find_victim_big(img):

	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Here, the matter is straight forward. If pixel value is greater than a threshold value, 
	# it is assigned one value (may be white), else it is assigned another value (may be black). 
	#The function used is cv2.threshold. First argument is the source image, which should be a grayscale image.
	# Second argument is the threshold value which is used to classify the pixel values. 
	# Third argument is the maxVal which represents the value to be given if pixel value is more than
	#  (sometimes less than) the threshold value. OpenCV provides different styles of thresholding and 
	#  it is decided by the fourth parameter of the function. Different types are:
	# 		cv2.THRESH_BINARY
	# 		cv2.THRESH_BINARY_INV
	# 		cv2.THRESH_TRUNC
	# 		cv2.THRESH_TOZERO
	# 		cv2.THRESH_TOZERO_INV

	ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

	# Contours can be explained simply as a curve joining all the continuous points (along the boundary),
	# having same color or intensity. The contours are a useful tool for shape analysis and object detection and recognition.
	contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	for cnt in contours:
		x,y,w,h = cv2.boundingRect(cnt)
		#bound the images
		cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
	i=0
	victims=[]
	for cnt in contours:
		x,y,w,h = cv2.boundingRect(cnt)
		#following if statement is to ignore the noises and save the images which are of normal size(character)
		#In order to write more general code, than specifying the dimensions as 100,
		# number of characters should be divided by word dimension
		if w>100 and w<130 and h>100 and h<130:
			#save individual images
			victims.append((x,y,h,w))
			i=i+1

	return victims

def find_victim(img):

	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Here, the matter is straight forward. If pixel value is greater than a threshold value, 
	# it is assigned one value (may be white), else it is assigned another value (may be black). 
	#The function used is cv2.threshold. First argument is the source image, which should be a grayscale image.
	# Second argument is the threshold value which is used to classify the pixel values. 
	# Third argument is the maxVal which represents the value to be given if pixel value is more than
	#  (sometimes less than) the threshold value. OpenCV provides different styles of thresholding and 
	#  it is decided by the fourth parameter of the function. Different types are:
	# 		cv2.THRESH_BINARY
	# 		cv2.THRESH_BINARY_INV
	# 		cv2.THRESH_TRUNC
	# 		cv2.THRESH_TOZERO
	# 		cv2.THRESH_TOZERO_INV

	ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

	# Contours can be explained simply as a curve joining all the continuous points (along the boundary),
	# having same color or intensity. The contours are a useful tool for shape analysis and object detection and recognition.
	contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	for cnt in contours:
		x,y,w,h = cv2.boundingRect(cnt)
		#bound the images
		cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
	i=0
	victims=[]
	img_h,img_w = img.shape
	for cnt in contours:
		x,y,w,h = cv2.boundingRect(cnt)
		#following if statement is to ignore the noises and save the images which are of normal size(character)
		#In order to write more general code, than specifying the dimensions as 100,
		# number of characters should be divided by word dimension
		if (img_w - w)<20 or (img_h - h)<20:
			continue
		if w<20 or h<20:
			continue
			#save individual images
		victims.append((x,y,h,w))
		print((x,y,h,w))
		i=i+1

	print(len(victims))
	return victims


img = cv2.imread('img/vision.png')  # Read image file
print("Vision image size: ", img.shape) #(860, 1321, 3)


victims = find_victim_big(img)

if len(victims)> 0:
  x,y,h,w = victims[0]

  img = cv2.rectangle(img, (x,y), (x+w,y+h), color=(255, 0, 0), thickness=4) 

else:
   print("No victim found!")

plt.subplot(111), plt.imshow(img, cmap='gray'), plt.title('Victim')  # Plot the Image
plt.show()  # Show the plotter window (You should see the image in a new window now)
