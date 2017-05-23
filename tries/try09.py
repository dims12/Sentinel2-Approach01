import boto3

# s3 = boto3.resource('s3', region_name='us-east-2')
# bucket = s3.Bucket('sentinel-s2-l1c')
# object = bucket.Object('tiles/10/S/DG/')
# for str in object.get_available_subresources():
#     print(str)


import boto3
bucket = 'sentinel-s2-l1c'
prefix = 'tiles/10/S/DG/'

client = boto3.client('s3', region_name='us-east-2')
result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
subdirs = result['CommonPrefixes']
for prefix in subdirs:
    print( 'subdir: ', prefix['Prefix'] )