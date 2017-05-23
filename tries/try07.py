import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import boto3
import mgrs
import re
from PIL import Image

img = mpimg.imread('gladiolus.jpg')
img = np.divide(img, 255)
imgplot = plt.imshow(img)
plt.show(imgplot)

pass