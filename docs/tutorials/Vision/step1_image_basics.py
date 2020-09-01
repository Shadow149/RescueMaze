"""
Example OpenCV basics
Written by Fatemeh Pahlevan Aghababa, Amirreza Kabiri, MohammadHossein Goharinejad - 2020

"""

################################
##  OpenCV
################################
# OpenCV is one the greated libraries for machine vision,
# Although we can not cover all concepts of this library here
# But we trying to show you basic operation and most useful functions in this project


# pip install 
import cv2
import numpy
import matplotlib.pyplot as plt

# Core Functions
img = cv2.imread('img/vision.png')  # Read image file
print("Vision image size: ", img.shape) #(860, 1321, 3)

plt.subplot(111), plt.imshow(img, cmap='gray'), plt.title('Vision')  # Plot the Image
plt.show()  # Show the plotter window (You should see the image in a new window now)

# You can access a pixel value by its row and column coordinates. For BGR(Blue,Green,red) image,
# it returns an array of Blue, Green, Red values.
# For grayscale image, just corresponding intensity is returned.
px = img[100, 100]
print(px)  # => [105 105 105]
# accessing only blue pixel
blue = img[100, 100, 0]
print(blue)  # => 105

# You can modify the pixel values the same way.
img[100, 100] = [255, 255, 255]
print(img[100, 100])  # => [255 255 255]

### NOTICE
##
# Numpy is a optimized library for fast array calculations.
# So simply accessing each and every pixel values and modifying it will be very slow and it is discouraged.
##
###

### NOTICE
##
# Above mentioned method is normally used for selecting a region of array,
# say first 5 rows and last 3 columns like that. For individual pixel access,
# Numpy array methods, array.item() and array.itemset() is considered to be better.
# But it always returns a scalar.
#
# So if you want to access all B,G,R values,
# you need to call array.item() separately for all.
##
###

### Better pixel accessing and editing method :
## accessing RED value
img.item(10, 10, 2)  # => 167

## modifying RED value
img.itemset((10, 10, 2), 100)
img.item(10, 10, 2)  # => 100

### Accessing Image Properties
## Image properties include number of rows, columns and channels, type of image data, number of pixels etc.

## Shape of image is accessed by img.shape. It returns a tuple of number of rows, columns and channels (if image is color):
print(img.shape)

# Total number of pixels is accessed by img.size:
print(img.size)

# Image datatype is obtained by img.dtype:
print(img.dtype)


### Splitting and Merging Image Channels
# The B,G,R channels of an image can be split into their individual planes when needed.
# Then, the individual channels can be merged back together to form a BGR image again.
# This can be performed by:
b, g, r = cv2.split(img)
img = cv2.merge((b, g, r))

## Or ##
b = img[:, :, 0]

# Suppose, you want to make all the red pixels to zero,
# you need not split like this and put it equal to zero.
# You can simply use Numpy indexing which is faster.
img[:, :, 2] = 0

#### Warning ####
# `cv2.split()` is a costly operation (in terms of time),
# so only use it if necessary.
# Numpy indexing is much more efficient and should be used if possible.
