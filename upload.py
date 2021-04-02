import os
import boto3
import sys
from jproperties import Properties
import random
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from datetime import date

UPLOAD_FOLDER = 'D://Dalhousie'

app = Flask(__name__)
maximum = sys.maxsize
a = 715968128483455541
app.secret_key = os.urandom(24)
config = Properties()
region_name = "us-east-1"
with open('aws.properties', 'rb') as read:
    config.load(read)

aws_access_key_id = config.get("AWS_ACCESS_KEY_ID").data
aws_secret_access_key = config.get("AWS_SECRET_ACCESS_KEY").data
aws_session_token = config.get("AWS_SESSION_TOKEN").data

print(aws_access_key_id)
print(aws_secret_access_key)
print(aws_session_token)

# today = date.today().strftime("%d/%m/%Y")
# dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key_id,
#                         aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
# table = dynamo.Table('converter')
# id_value = []
# print(table)
# response = table.scan()
# print(response['Items'])
# for i in response['Items']:
#     id_value.append(i['id'])
# while random_val in id_value:
#     random_val = random.randint(0, maximum)
# print(response)
# print(id_value)


@app.route('/upload', methods=['GET', 'POST'])
def getDetails():
    random_val = random.randint(0, maximum)
    today = date.today().strftime("%d/%m/%Y")
    dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    table = dynamo.Table('converter')
    id_value = []
    print(table)
    response = table.scan()
    print(response['Items'])
    for i in response['Items']:
        id_value.append(i['id'])
    while random_val in id_value:
        random_val = random.randint(0, maximum)
    print(response)
    print(id_value)

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
                     'file': filename}

            path = 'D://Dalhousie//' + filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            s3 = boto3.resource(service_name='s3',
                                region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                aws_session_token=aws_session_token)
            s3.Bucket('mp3filebucket').upload_file(Filename=path, Key=filename)
            print(filename)
            print(email)
            print('done')
            table.put_item(Item=trans)
    return "its done"
