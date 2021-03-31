import os
import boto3
from jproperties import Properties
from flask import Flask,render_template,request,redirect,session

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

dynamo = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id = aws_access_key_id,aws_secret_access_key = aws_secret_access_key,aws_session_token=aws_session_token)
