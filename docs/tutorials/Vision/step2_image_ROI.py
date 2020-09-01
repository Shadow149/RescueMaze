"""
Example OpenCV ROI
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

### Image ROI
# Sometimes, you will have to play with certain region of images.
# For eye detection in images,
# first perform face detection over the image until the face is found,
# then search within the face region for eyes.
# This approach improves accuracy (because eyes are always on faces :D ) 
# and performance (because we search for a small area).

## ROI is again obtained using Numpy indexing.
## Here I am selecting the ball and copying it to another region in the image:
box = img[250:750, 100:600]
img[250:750, 650:1150] = box

# Check the results below:
plt.subplot(111), plt.imshow(img, cmap='gray'), plt.title('ROI')  # Plot the Image
plt.show()  # Show the plotter window (You should see the image in a new window now)

"""    Image ROI    """
