# This example shows how to read tile file from Sentinel 2 bucket

import boto3
s3 = boto3.resource('s3', region_name='us-east-2')
bucket = s3.Bucket('sentinel-s2-l1c')
object = bucket.Object('tiles/10/S/DG/2015/12/7/0/B01.jp2')
object.download_file('B01.jp2')

pass