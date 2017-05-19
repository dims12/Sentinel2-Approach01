# This example shows how to read tile file from Sentinel 2 bucket
# and show it

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import boto3
s3 = boto3.resource('s3', region_name='us-east-2')

bucket = s3.Bucket('sentinel-s2-l1c')

object = bucket.Object('tiles/10/S/DG/2015/12/7/0/tileInfo.json')
object.download_file('tileInfo.json')

object = bucket.Object('tiles/10/S/DG/2015/12/7/0/metadata.xml')
object.download_file('metadata.xml')

object = bucket.Object('tiles/10/S/DG/2015/12/7/0/B01.jp2')
object.download_file('B01.jp2')


img=mpimg.imread('B01.jp2')
imgplot = plt.imshow(img, cmap=plt.cm.gray)
plt.show(imgplot)

pass