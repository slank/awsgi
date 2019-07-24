=====
AWSGI
=====

A WSGI adapter for AWS API Gateway/Lambda Proxy Integration
===========================================================

AWSGI allows you to use WSGI-compatible middleware and frameworks like Flask and Django with the `AWS API Gateway/Lambda proxy integration <https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html>`_.

Installation
------------

``awsgi`` is available from PyPI as ``aws-wsgi``::

    pip install aws-wsgi

Example
-------

.. code-block:: python

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
        return awsgi.response(app, event, context, base64_content_types={"image/png"})
