import matplotlib.image as mpimg
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

print('Reading B04.jp2...')
img_red = mpimg.imread('B04.jp2')

print('Reading B03.jp2...')
img_green = mpimg.imread('B03.jp2')

print('Reading B02.jp2...')
img_blue = mpimg.imread('B02.jp2')

img = np.dstack((img_red, img_green, img_blue))

img = np.divide(img, 64)
img = img.astype(np.uint8)

print('Saving MIX.jpeg...')
mpimg.imsave('MIX.jpeg', img, format='jpg')

