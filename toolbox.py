# LIBCAMERA_LOG_LEVELS=WARN python toolbox.py

from datetime import datetime
import logging
import os
from time import sleep
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from picamera2 import Picamera2

CAPTURE_DELAY=10
BUCKET="sgaze-rpi-cctv"

def publish_s3(file_name, bucket):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :return: True if file was uploaded, else False
    """

    object_name = os.path.basename(file_name)

    # Upload the file
    my_config = Config(
        region_name='eu-west-1'
    )
    s3_client = boto3.client('s3', config=my_config)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as s3_exception:
        logging.error(s3_exception)
        return False
    return True

def capture_file(file_name):
    print("running autofocus...")
    autofocus_success = camera.autofocus_cycle()
    print("autofocus done", autofocus_success)

    print("capturing file...")
    capture_success = camera.switch_mode_and_capture_file(
        configuration, file_name, name="main", wait=True)
    print("capture done")

    print("uploading file", file_name, "to", BUCKET, "...")
    s3_success = publish_s3(file_name, BUCKET)
    print("upload done", s3_success)

    print("deleting file", file_name, "...")
    if os.path.isfile(file_name):
        os.remove(file_name)
        print("file deleted", file_name)
    else:
        print("Error: %s file not found" % file_name)


Picamera2.set_logging(Picamera2.ERROR)

camera = Picamera2()
camera.options["quality"] = 50
configuration = camera.create_still_configuration(main={"size": (1280, 720)})

try:
     while True:
        FILE_NAME = "rpi-cctv_" + str(datetime.now()) + ".jpg"

        camera.start()
        capture_file(FILE_NAME)
        sleep(CAPTURE_DELAY)
        camera.stop()

except KeyboardInterrupt:
    pass

except Exception as err:
    raise err
