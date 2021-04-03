import os
import boto3
import sys
from jproperties import Properties
import random
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from datetime import date
import json
import requests

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

dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

s3 = boto3.resource(service_name='s3',
                    region_name=region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token)

sns = boto3.client('sns',
                   region_name=region_name,
                   aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   aws_session_token=aws_session_token)
email = ''
response = sns.list_topics()
topics = response["Topics"]

print(f'topics are {topics}')
for arn in topics:
    # print(arn['TopicArn'])
    if 'dynamodb' not in arn['TopicArn']:
        continue
    else:
        topic_arn = arn['TopicArn']
        # print(f'topic_arn is {topic_arn}')
        # print(type(topic_arn))
# topic_arn = topics["TopicArn"]
# print(f'topic_arn is {topic_arn}')
trans = {}

# response = sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint="user@server.com")
# subscription_arn = response["SubscriptionArn"]

print(aws_access_key_id)
print(aws_secret_access_key)
print(aws_session_token)


@app.route('/upload', methods=['GET', 'POST'])
def getDetails():
    random_val = random.randint(0, maximum)
    today = date.today().strftime("%d/%m/%Y")
    table = dynamo.Table('converter')
    id_value = []
    data = {}
    response = None
    print(table)
    responses = table.scan()
    print(responses['Items'])
    for i in responses['Items']:
        id_value.append(i['id'])
    while random_val in id_value:
        random_val = random.randint(0, maximum)
    print(responses)
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
                     'file': filename,
                     'status': 1}

            path = 'D://Dalhousie//' + filename
            key = str(random_val) + '_' + filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            s3 = boto3.resource(service_name='s3',
                                region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                aws_session_token=aws_session_token)
            s3.Bucket('mp3filebucket').upload_file(Filename=path, Key=key)
            print(filename)
            print(email)
            print('done')
            data = {'email': email,
                    'id': random_val
                    }
            table.put_item(Item=trans)
            params = {'key': key, 'bucket': 'mp3filebucket', 'email': email}
            url = 'http://54.175.220.48:8080'
            response_post = requests.post(url, params)
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
    return response


@app.route('/mail', methods=['GET', 'POST'])
def sendEmail():
    print(topic_arn)
    bucket = request.form.get('bucket')
    key = request.form.get('key')
    email = request.form.get('email')
    link = f'https://{bucket}.s3.amazonaws.com/{key}'
    response_sns = sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=email)
    subscription_arn = response_sns["SubscriptionArn"]
    sns.publish(TopicArn=topic_arn,
                Message=f"Hi, here is your link to download {link}",
                Subject="Link to download")
    return 'mail sent'
