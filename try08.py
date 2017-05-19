# This example shows how to read tile file from Sentinel 2 bucket
# and show it

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import boto3
import mgrs
import re
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

s3 = boto3.resource('s3', region_name='us-east-2')

longitude = 37.593947
latitude = 55.731979

m = mgrs.MGRS()

mgrs = m.toMGRS(latitude, longitude).decode('cp1252')

s = re.search('(\d+)([^\d])([^\d]{2})(\d{5})(\d{5})', mgrs)

UTM = s.group(1)
LatitudeBand = s.group(2)
Square = s.group(3)

bucket = s3.Bucket('sentinel-s2-l1c')

tilesdir = 'tiles/' + UTM + '/'+ LatitudeBand + '/' + Square + '/'

datestring = '2017/5/10/0/'

filename = 'tileInfo.json'
object = bucket.Object(tilesdir + datestring + filename)
object.download_file(filename)

filename = 'metadata.xml'
object = bucket.Object(tilesdir + datestring + filename)
object.download_file(filename)

filename = 'B02.jp2'
object = bucket.Object(tilesdir + datestring + filename)
object.download_file(filename)

filename = 'B03.jp2'
object = bucket.Object(tilesdir + datestring + filename)
object.download_file(filename)

filename = 'B04.jp2'
object = bucket.Object(tilesdir + datestring + filename)
object.download_file(filename)


img_blue = np.divide(mpimg.imread('B02.jp2'), 65535)
img_green = np.divide(mpimg.imread('B03.jp2'), 65535)
img_red = np.divide(mpimg.imread('B04.jp2'), 65535)
img = np.dstack((img_red,img_green,img_blue))


imgplot = plt.imshow(img)
plt.show(imgplot)

pass