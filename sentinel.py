import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import mgrs
import re
import boto3
from PIL import Image
import datetime
import os.path
import numpy as np
import utm
import sys

Image.MAX_IMAGE_PIXELS = 1000000000

bucket_name = 'sentinel-s2-l1c'
s3_resource = boto3.resource('s3', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')
bucket = s3_resource.Bucket(bucket_name)

# EarthRadius = 6371008.8
#
# # earth equatorial radius
# a = 6378.137
#
# # inverse flattening
# f_inv = 298.257223563
#
# # flattening
# f = 1./f_inv
#
# N_north = 0
# N_south = 10000
# k0 = 0.9996
# E0 = 500
#
# n = f / (2 - f)
#
# A = a / (1 + n) * (1 + n/4*n + n/64*n*n*n)
#
# alpha1 = n/2 - 2*n/3*n + 5*n/16*n*n
#
# alpha2 = 13*n/48*n - 3*n/5*n*n
#
# alpha3 = 61*n/240*n*n
#
# beta1 = n / 2 - 2*n/3*n + 37*n/96*n*n
#
# beta2 = n/48*n + n/15*n*n
#
# beta3 = 17 * n / 480 *n *n
#
# delta1 = 2*n -2*n/3*n - 2*n*n*n
#
# delta2 = 7*n/3*n - 8*n/5*n*n
#
# delta3 = 56*n/15*n*n

m = mgrs.MGRS()

def retrieveSubdirectories(root):
    result = s3_client.list_objects(Bucket=bucket_name, Prefix=root, Delimiter='/')
    preans = result['CommonPrefixes']
    return [prefix['Prefix'] for prefix in preans]

def cacheObject(path):
    object = bucket.Object(path)
    if not os.path.isfile(path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        object.download_file(path)

def loadJson(path):
    cacheObject(path)

    #file_content = object.get()['Body'].read().decode('utf-8')
    with open(path) as data_file:
        ans = json.load(data_file)

    return ans

def loadImage(path):
    cacheObject(path)

    img = mpimg.imread(path)
    return img

def cropNdarray(img, tile_width, tile_height, centerx, centery, width, height):
    image_height, image_width = img.shape
    startx = centerx - width/2
    endx = startx + width

    startx = int(startx * image_width / tile_width)
    endx = int(endx  * image_width / tile_width)


    if startx < 0:
        startx = 0
    if endx > image_width:
        endx = image_width

    starty = centery - height/2
    endy = starty + height

    starty = int(starty * image_height / tile_height)
    endy = int(endy * image_height / tile_height)

    if starty < 0:
        starty = 0
    if endy > image_height:
        endy = image_height

    return img[starty:endy, startx:endx]

class SentinelAddress:

    def __init__(self, latitude, longitude, start_date=None):

        self.Longitude = longitude
        self.Latitude = latitude
        self.StartDate = start_date

        #self.LatitudeCircleRadius = EarthRadius * math.cos(math.radians(latitude))

        self.mgrs = m.toMGRS(latitude, longitude).decode('cp1252')

        s = re.search('(\d+)([^\d])([^\d]{2})(\d{5})(\d{5})', self.mgrs)

        self.UTM = s.group(1)
        self.LatitudeBand = s.group(2)
        self.Square = s.group(3)

        self.TilePathBase = 'tiles/' + self.UTM + '/' + self.LatitudeBand + '/' + self.Square + '/'

        self.CentralMeridian = (int(self.UTM) - 1) * 6 + 3 - 180
        self.Easting, self.Northing, UTM2, LatitudeBand2 = utm.from_latlon(latitude, longitude)



    def retrieveTileInfos(self):
        ans = {}

        for year_path in retrieveSubdirectories(self.TilePathBase):
            year = int( os.path.basename(os.path.normpath(year_path)))
            for month_path in retrieveSubdirectories(year_path):
                month = int(os.path.basename(os.path.normpath(month_path)))
                for day_path in retrieveSubdirectories(month_path):
                    day = int(os.path.basename(os.path.normpath(day_path)))
                    d = datetime.date(year, month, day)

                    if (self.StartDate is None) or (d >= self.StartDate):
                        for seq_path in retrieveSubdirectories(day_path):

                            print("Retrieving info for " + seq_path)

                            tileInfo = loadJson(seq_path + 'tileInfo.json')

                            descr = {'path': seq_path, 'tileInfo': tileInfo}

                            if d in ans:
                                ans[d].append(descr)
                            else:
                                ans[d] = [descr]

        return ans

    def getTargetDirectory(self):
        if self.Latitude >= 0:
            latstr = "N%010.7f" % (self.Latitude,)
        else:
            latstr = "S%010.7f" % (-self.Latitude,)

        if self.Longitude >= 0:
            lngstr = "E%010.7f" % (self.Longitude,)
        else:
            lngstr = "W%010.7f" % (-self.Longitude,)
        return 'results/' + latstr + '_' + lngstr + '/'

    def retrieveCrops(self, size, *filenames):
        infos = self.retrieveTileInfos()
        for d, info in infos.items():
            coords = info[0]['tileInfo']['tileGeometry']['coordinates'][0]
            path = info[0]['path']
            cloudyPixelPercentage = info[0]['tileInfo']['cloudyPixelPercentage']

            if cloudyPixelPercentage < 50:
                images = ()

                targetfilename = self.getTargetDirectory() + d.strftime('%Y%m%d') + '.jpg'
                if not os.path.exists(os.path.dirname(targetfilename)):
                    os.makedirs(os.path.dirname(targetfilename))

                for filename in filenames:


                    print("Loading and cropping " + path + filename)

                    minx = min([c[0] for c in coords])
                    miny = min([c[1] for c in coords])
                    maxx = max([c[0] for c in coords])
                    maxy = max([c[1] for c in coords])

                    tile_width = maxx - minx
                    tile_height = maxy - miny

                    centerx = int(self.Easting - minx)
                    centery = int(maxy - self.Northing)

                    img = loadImage(path + filename)

                    img2 = cropNdarray(img, tile_width, tile_height, centerx, centery, size, size)

                    images = images + (img2,)

                multiimage = np.dstack(images)

                multiimage = np.divide(multiimage, 64)
                multiimage = multiimage.astype(np.uint8)

                print("Saving " + path + filename)
                mpimg.imsave(targetfilename, multiimage, format='jpg')
                # scipy.misc.imsave(targetfilename, img2)




def retrieveCrops(latitude, longitude, start_date, size):
    s = SentinelAddress(latitude, longitude, start_date)
    s.retrieveCrops(size, 'B04.jp2', 'B03.jp2', 'B02.jp2')


# St. Basel
# latitude = 55.752442
# longitude = 37.623172

# # tanks
# latitude = 32.07910197387007
# longitude = -103.17672729492188

if len(sys.argv) == 5:

    latitude = float(sys.argv[1])
    longitude = float(sys.argv[2])


    start_date = datetime.datetime.strptime(sys.argv[3], '%Y%m%d').date()

    size = int(sys.argv[4])

    retrieveCrops(latitude, longitude, start_date, size)

else:
    print('Usage:\nsentinel latitude longitude start_date size')















