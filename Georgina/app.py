from flask import Flask, config, request, jsonify, render_template
import os
import boto3
from botocore.config import Config

app = Flask(__name__)

# app_config = Config(
#     region_name = 'us-east-1'
# )

# db_data = boto3.client('db_data', config=app_config, aws_access_key_id='TODO', aws_secret_access_key='TODO')

# db_name = 'TODO'
# db_cluster_arn = 'TODO'
# db_secret_arn = 'TODO'

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/forum')
def getPosts():
    return render_template("forum_posts.html")

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)