=====
AWSGI
=====

A WSGI adapter for AWS API Gateway/Lambda Proxy Integration
===========================================================

AWSGI allows you to use WSGI-compatible middleware and frameworks like Flask and Django with the AWS API Gateway/Lambda proxy integration.

Example
-------

::

    import awsgi
    from flask import (
        Flask,
        jsonify,
    )
    
    app = Flask(__name__)
    
    
    @app.route('/')
    def index():
        return jsonify(status=200, message='OK')
    
    def lambda_handler(event, context):
        return awsgi.response(app, event, context)
