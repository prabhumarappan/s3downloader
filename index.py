import os
import boto3
import getpass
import requests
import datetime as dt
from threading import Thread
from flask import Flask, render_template, request, redirect, flash

username = getpass.getuser()
STORAGE_PATH ='/home/%s/s3/'%(username)
ROOT_S3 = "uploads"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
REGION_HOST = ''

bucket_name = ''

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

if not os.path.isdir(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

app = Flask(__name__, static_url_path="/static")
        
def download_file(file_key, folder_key):
    file_name = file_key.split("/")[-1]

    output_file = os.path.join(STORAGE_PATH, folder_key, file_name)
    s3.download_file(bucket_name, file_key, output_file)

def download_folder(folder_name, folder_key, previous_folder=None):    
    if previous_folder is None:
        previous_folder = folder_name
    else:
        previous_folder = os.path.join(previous_folder, folder_name)

    download_path = os.path.join(STORAGE_PATH, previous_folder)
    if not os.path.isdir(download_path):
        os.makedirs(download_path)
    
    folder_key = "%s%s/"%(folder_key, folder_name)

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key, Delimiter="/")

    if 'Contents' in response:
        output = response['Contents']
        for sel in output:
            file_key = sel['Key']
            download_file(file_key, previous_folder)
    elif 'CommonPrefixes' in response:
        output = response['CommonPrefixes']
        output = [x['Prefix'].split("/")[-2] for x in output]
        for sel in output:
            download_folder(sel, folder_key, previous_folder)

@app.route("/")
def index():
    return redirect("/uploads")

@app.route('/download', methods=['POST'])
def download():
    request_origin = request.environ['HTTP_REFERER']
    request_data = request.form.getlist('fname')

    folder_key =  request_origin.split('http://127.0.0.1:5000/')[-1]

    thread_list = []

    for sel in request_data:
        sel = str(sel)
        fol = Thread(target=download_folder, args=(sel, folder_key))
        fol.start()
    
    return ('', 204)

@app.route('/', defaults={'path': '/'})
@app.route('/<path:path>/')
def fetch(path):
    if not path.endswith("/"):
        name = "%s/"%(path)
    else:
        name = "%s"%(path)

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=name, Delimiter="/")
    files = False
    output = []
    if 'Contents' in response:
        files = True
        output = response['Contents']
        output = [x['Key'].split("/")[-1] for x in output]
    elif 'CommonPrefixes' in response:
        output = response['CommonPrefixes']
        output = [x['Prefix'].split("/")[-2] for x in output]
    else:
        file_key = response['Prefix'].strip("/")
        file_name = file_key.split("/")[-1]
        file_name = os.path.join(STORAGE_PATH, file_name)
        s3.download_file(bucket_name, file_key, file_name)

        return ('', 204)
    
    return render_template("index.html", datalist=output, files=files)

if __name__ == "__main__":
    app.run()