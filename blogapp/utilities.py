import os
import mimetypes
from functools import wraps
from datetime import datetime

import boto3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from flask import redirect, session, current_app

additional_file_types = {
    ".md": "text/markdown"
}


class S3BucketUtils:
    """Useful methods to connect flask with amazon s3 buckets"""

    @classmethod
    def get_s3_session(cls):
        s3_key = current_app.config["S3_KEY"]
        s3_secret = current_app.config["S3_SECRET"]
        if s3_key and s3_secret:
            return boto3.Session(
                aws_access_key_id=s3_key,
                aws_secret_access_key=s3_secret)
        else:
            return boto3.Session()

    @classmethod
    def get_s3_resource(cls):
        return cls.get_s3_session().resource("s3")
    
    @classmethod
    def get_bucket(cls, use_temp=False):
        s3_resource = S3BucketUtils.get_s3_resource()
        s3_bucket = current_app.config["S3_BUCKET"]
        if use_temp:
            s3_bucket = current_app.config["S3_BUCKET_TEMP"]
        return s3_resource.Bucket(s3_bucket)
    
    @classmethod
    def get_bucket_list(cls):
        client = cls.get_s3_session().client("s3")
        
        return client.list_buckets().get("Buckets")


def login_required(f):
    """Decorate routes to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def file_type(key):
    """Return file extension of given file"""
    file_info = os.path.splitext(key)
    file_extension = file_info[1]
    try:
        return mimetypes.types_map[file_extension]
    except KeyError:
        filetype = "Unknown"
        if file_info[0].startswith(".") and file_extension == "":
            filetype = "text"
        
        if file_extension in additional_file_types.keys():
            filetype = additional_file_types[file_extension]
        
        return filetype


def make_unique_url(filename):
    """Add timestamp including millisecnds to make filename unique"""
    file_info = os.path.splitext(filename)
    file_extension = file_info[1]
    filename = file_info[0] + "-" + datetime.now().strftime('%Y%m%d%H%M%S%f')
    return filename + file_extension


def extract_img_url(page_data):
    """Given html data, return all occurrences of img src's"""
    soup = BeautifulSoup(page_data, "html.parser")

    images = []
    for img in soup.findAll("img"):
        images.append(img.get("src"))

    return images


def extract_key_from_url(url):
    """Given an s3 object url, return the key (filename)"""
    return urlparse(url).path.strip("/")


# Credits: https://stackoverflow.com/questions/22105315/flask-getting-the-size-of-each-file-in-a-request
def get_size(fobj):
    """Get file upload size for validation"""
    if fobj.content_length:
        return fobj.content_length

    try:
        pos = fobj.tell()
        fobj.seek(0, 2)  #seek to end
        size = fobj.tell()
        fobj.seek(pos)  # back to original position
        return size
    except (AttributeError, IOError):
        pass

    # in-memory file object that doesn't support seeking or tell
    return 0  #assume small enough


def replace_img_src(content: str) -> str:
    """Replace img src with new src from bucket transfer"""

    # Transfer images from temp to actual bucket.
    soup = BeautifulSoup(content, "html.parser")
    client = S3BucketUtils.get_s3_session().client("s3")
    bucket_temp = S3BucketUtils.get_bucket(use_temp=True)
    bucket_dest = S3BucketUtils.get_bucket()

    for img in soup.findAll("img"):
        key = extract_key_from_url(img["src"])
        copy_source = {
            "Bucket": bucket_temp.name,
            "Key": key
        }

        # Don't do anything with image that wasn't changed.
        if "temp" not in urlparse(img["src"]).netloc:
            continue

        client.copy_object(   # copy to other bucket
            Bucket=bucket_dest.name, CopySource=copy_source, Key=key)
        bucket_temp.Object(key).delete()  # delete from old bucket
        img["src"] = f"https://flask-bruhlog.s3.us-west-1.amazonaws.com/{key}"
    
    return str(soup)

