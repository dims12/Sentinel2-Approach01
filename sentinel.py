import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import math
import mgrs
import re
import boto3
from PIL import Image
import datetime
import os.path
import numpy as np

Image.MAX_IMAGE_PIXELS = 1000000000

bucket_name = 'sentinel-s2-l1c'
s3_resource = boto3.resource('s3', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')
bucket = s3_resource.Bucket(bucket_name)

EarthRadius = 6371008.8
m = mgrs.MGRS()

def retrieveSubdirectories(root):
    result = s3_client.list_objects(Bucket=bucket_name, Prefix=root, Delimiter='/')
    preans = result['CommonPrefixes']
    return [prefix['Prefix'] for prefix in preans]

def loadJson(path):
    object = bucket.Object(path)
    file_content = object.get()['Body'].read().decode('utf-8')
    ans = json.loads(file_content)
    return ans

def loadImage(path):
    object = bucket.Object(path)
    filename = os.path.basename(os.path.normpath(path))
    object.download_file(filename)
    img = mpimg.imread(filename)
    os.remove(filename)
    return img

def cropNdarray(img, centerx, centery, width, height):
    imageHeight,imageWidth = img.shape
    startx = int(centerx - width/2)
    endx = startx + width

    if startx < 0:
        startx = 0
    if endx > imageWidth:
        endx = imageWidth

    starty = int(centery - height/2)
    endy = starty + height

    if starty < 0:
        starty = 0
    if endy > imageHeight:
        endy = imageHeight

    return img[starty:endy, startx:endx]

class SentinelAddress:

    def __init__(self, latitude, longitude):

        self.Longitude = longitude
        self.Latitude = latitude

        self.LatitudeCircleRadius = EarthRadius * math.cos(math.radians(latitude))

        self.mgrs = m.toMGRS(latitude, longitude).decode('cp1252')

        s = re.search('(\d+)([^\d])([^\d]{2})(\d{5})(\d{5})', self.mgrs)

        self.UTM = s.group(1)
        self.LatitudeBand = s.group(2)
        self.Square = s.group(3)

        self.TilePathBase = 'tiles/' + self.UTM + '/' + self.LatitudeBand + '/' + self.Square + '/'

        self.CentralMeridian = (int(self.UTM) - 1) * 6 + 3 - 180
        self.Easting = math.radians(longitude - self.CentralMeridian) * self.LatitudeCircleRadius + 500000
        self.Northing = math.radians(latitude) * EarthRadius
        if self.Northing < 0:
            self.Northing += 10000000



    def retrieveTileInfos(self):
        ans = {}

        for year_path in retrieveSubdirectories(self.TilePathBase):
            year = int( os.path.basename(os.path.normpath(year_path)))
            for month_path in retrieveSubdirectories(year_path):
                month = int(os.path.basename(os.path.normpath(month_path)))
                for day_path in retrieveSubdirectories(month_path):
                    day = int(os.path.basename(os.path.normpath(day_path)))
                    d = datetime.date(year, month, day)
                    for seq_path in retrieveSubdirectories(day_path):

                        print("Retrieving info for " + seq_path)

                        tileInfo = loadJson(seq_path + 'tileInfo.json')

                        descr = {'path': seq_path, 'tileInfo': tileInfo}

                        if d in ans:
                            ans[d].append(descr)
                        else:
                            ans[d] = [descr]

        return ans

    def retrieveCrops(self, filename, size):
        infos = self.retrieveTileInfos()
        for d, info in infos.items():
            coords = info[0]['tileInfo']['tileGeometry']['coordinates'][0]
            path = info[0]['path']
            targetfilename = d.strftime('%Y%m%d' + filename)
            targetfilename = os.path.splitext(targetfilename)[0] + '.jpg'

            print("Cropping " + path + filename)

            minx = min([c[0] for c in coords])
            miny = min([c[1] for c in coords])
            maxx = max([c[0] for c in coords])
            maxy = max([c[1] for c in coords])

            centerx = int(self.Easting - minx)
            centery = int(maxy - self.Northing)

            img = loadImage(path + filename)
            imageHeight, imageWidth = np.shape(img)


            img2 = cropNdarray(img, centerx, centery, size, size)

            mpimg.imsave(targetfilename, img2, format='jpg', cmap=plt.cm.gray)
            # scipy.misc.imsave(targetfilename, img2)

            print("Saved ", targetfilename)



latitude = 55.752486
longitude = 37.623199

s = SentinelAddress(latitude, longitude)

s.retrieveCrops('B02.jp2', 100)










