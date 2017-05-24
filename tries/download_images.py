import boto3

# s3 = boto3.resource('s3', region_name='us-east-2', aws_access_key_id='AKIAIJDWSJYWKQDPQPFQ',
#          aws_secret_access_key='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')

s3 = boto3.resource('s3', region_name='us-east-2')


bucket = s3.Bucket('sentinel-s2-l1c')
#path = 'tiles/36/R/UU/2017/5/14/0/' # pyramides
path = 'tiles/18/Q/TM/2017/5/3/0/' # Bagamas

print('Loading B02.jp2')
object = bucket.Object(path + 'B02.jp2')
object.download_file('B02.jp2')

print('Loading B03.jp2')
object = bucket.Object(path + 'B03.jp2')
object.download_file('B03.jp2')

print('Loading B04.jp2')
object = bucket.Object(path + 'B04.jp2')
object.download_file('B04.jp2')

