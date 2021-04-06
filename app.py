import json
import os
import random
import sys
from datetime import date

import boto3
import requests
from flask import Flask, request, redirect, flash
from jproperties import Properties
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
BUCKET = 'cloudofduty'
app = Flask(__name__)
maximum = sys.maxsize
app.secret_key = os.urandom(24)
config = Properties()
region_name = "us-east-1"
with open('aws.properties', 'rb') as read:
    config.load(read)

aws_access_key_id = config.get("AWS_ACCESS_KEY_ID").data
aws_secret_access_key = config.get("AWS_SECRET_ACCESS_KEY").data
aws_session_token = config.get("AWS_SESSION_TOKEN").data

dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

s3 = boto3.resource(service_name='s3',
                    region_name=region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token)

email = ''
trans = {}


@app.route('/upload', methods=['GET', 'POST'])
def getDetails():
    random_val = random.randint(0, maximum)
    today = date.today().strftime("%d/%m/%Y")
    table = dynamo.Table('converter')
    id_value = []
    data = {}
    response = None
    responses = table.scan()
    for i in responses['Items']:
        id_value.append(i['id'])
    while random_val in id_value:
        random_val = random.randint(0, maximum)

    if request.method == 'POST':
        email = request.form.get('email', '')
        if 'file' not in request.files:
            flash('No file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            trans = {'id': random_val,
                     'email': email,
                     'date': today,
                     'file': filename,
                     'status': 1}

            path = "./uploads/"+filename
            key = str(random_val) + '_' + filename
            file.save(os.path.join("./uploads", filename))
            s3 = boto3.resource(service_name='s3',
                                region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                aws_session_token=aws_session_token)
            s3.Bucket(BUCKET).upload_file(Filename="./uploads/"+filename, Key=key)
            data = {'email': email,
                    'id': random_val
                    }
            table.put_item(Item=trans)
            params = {'key': key, 'bucket': BUCKET, 'email': email}
            url = 'https://glivwokrp2.execute-api.us-east-1.amazonaws.com'
            response_post = requests.post(url, params)
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
    return response

