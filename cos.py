import time
import ibm_boto3

from ibm_botocore.client import Config, ClientError

from django.conf import settings


def showMessage(msg):
	if settings.DEBUG:
		print(msg)


# Create the connection to our Cloud Object Storage (COS).
try:
	cos = ibm_boto3.resource('s3',
		ibm_api_key_id = settings.COS_API_KEY_ID,
		ibm_service_instance_id = settings.COS_RESOURCE_CRN,
		ibm_auth_endpoint = settings.COS_AUTH_ENDPOINT,
		endpoint_url = settings.COS_ENDPOINT,
		config = Config(signature_version='oauth')		
	)
except Exception as ex:
	msg = '>> Couldn\'t create Cloud Object Storage resource.\n>> Check your local_settings file to ensure you have the proper vars set.'
	#showMessage(msg)


def listFiles():
	msg = '>> Retrieving bucket contents from: {}\n'.format(settings.COS_BUCKET_NAME)
	try:
		files = cos.Bucket(settings.COS_BUCKET_NAME).objects.all()
		for file in files:
			msg +='>> Item: {} --- {} bytes\n'.format(file.key, file.size)
	except ClientError as be:
		msg += '>> CLIENT ERROR: {}\n'.format(be)
	except Exception as e:
		msg += '>> Unable to retrieve bucket contents: {}\n'.format(e)
	showMessage(msg)


def uploadFile(fileToUpload, cosFileName):
	msg = ''
	try:
		t0 = time.time()
		showMessage('>> Starting file transfer for {} to bucket: {}\n'.format(cosFileName, settings.COS_BUCKET_NAME))
		
		part_size = 1024 * 1024 * 5
		file_threshold = 1024 * 1024 * 20

		# Set the transfer threshold and chunk size
		transfer_config = ibm_boto3.s3.transfer.TransferConfig(
			multipart_threshold=file_threshold,
			multipart_chunksize=part_size
		)

		# The upload_fileobj method will automatically execute a multi-part upload
		# In 5 MB chunks for all files over 15 MB
		with open(fileToUpload, "rb") as file_data:
			cos.Object(settings.COS_BUCKET_NAME, cosFileName).upload_fileobj(
				Fileobj=file_data,
				Config=transfer_config
			)
			
		msg += '>> Transfer for {} complete!\n>> Took {}s'.format(cosFileName, round(time.time()-t0,1))
	except ClientError as be:
		msg = '>> CLIENT ERROR: {}'.format(be)
	except Exception as e:
		msg = '>> Unable to complete multi-part upload: {}'.format(e)
	showMessage(msg)


def getFile(fileName):
	msg = '>> Retrieving item from bucket: {}, key: {}\n'.format(settings.COS_BUCKET_NAME, fileName)
	try:
		return cos.Object(settings.COS_BUCKET_NAME, fileName).get()
		#msg += '>> File Contents: {}'.format(file["Body"].read())
	except ClientError as be:
		msg += '>> CLIENT ERROR: {}'.format(be)
	except Exception as e:
		msg += '>> Unable to retrieve file contents: {}'.format(e)
	showMessage(msg)


def deleteFile(fileName):
	msg = '>> Deleting item: {}'.format(fileName)
	try:
		cos.Object(settings.COS_BUCKET_NAME, fileName).delete()
		msg += '>> Item: {} deleted!'.format(fileName)
	except ClientError as be:
		msg += '>> CLIENT ERROR: {}'.format(be)
	except Exception as e:
		msg += '>> Unable to delete item: {}'.format(e)
	showMessage(msg)


# !! CAUTION !!
def deleteAllBucketFiles():
	for f in cos.Bucket(settings.COS_BUCKET_NAME).objects.all():
		deleteFile(f.key)




