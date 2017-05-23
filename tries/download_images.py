import boto3

s3 = boto3.resource('s3', region_name='us-east-2')
bucket = s3.Bucket('sentinel-s2-l1c')
path = 'tiles/36/R/UU/2017/5/14/0/'

object = bucket.Object(path + 'B02.jp2')
object.download_file('B02.jp2')
object = bucket.Object(path + 'B03.jp2')
object.download_file('B03.jp2')
object = bucket.Object(path + 'B04.jp2')
object.download_file('B04.jp2')

