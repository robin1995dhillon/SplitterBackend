import os
import boto3
from jproperties import Properties
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'D://Dalhousie'

app = Flask(__name__)
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


# dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id = aws_access_key_id,aws_secret_access_key = aws_secret_access_key,aws_session_token=aws_session_token)

@app.route('/upload', methods=['GET', 'POST'])
def getDetails():
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
    return "its done"
