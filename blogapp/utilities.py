import os
import mimetypes
from functools import wraps

import boto3
from flask import redirect, session, current_app

additional_file_types = {
    ".md": "text/mardown"
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
    def get_bucket(cls):
        s3_resource = S3BucketUtils.get_s3_resource()
        if "bucket" in session:
            s3_bucket = session["bucket"]
        else:
            s3_bucket = current_app.config["S3_BUCKET"]
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

