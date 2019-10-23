# -*- coding: utf-8 -*-
from io import BytesIO
import sys
import unittest
try:
    # Python 3
    from urllib.parse import urlencode

    # Convert bytes to str, if required
    def convert_str(s):
        return s.decode('utf-8') if isinstance(s, bytes) else s

    # Convert str to bytes, if required
    def convert_byte(b):
        return b.encode('utf-8', errors='strict') if (
            isinstance(b, str)) else b
except ImportError:
    # Python 2
    from urllib import urlencode

    # No conversion required
    def convert_str(s):
        return s

    # Convert str to bytes, if required
    def convert_byte(b):
        return b.encode('utf-8', errors='strict') if (
            isinstance(b, (str, unicode))) else b
import awsgi


class TestAwsgi(unittest.TestCase):
    def compareStringIOContents(self, a, b, msg=None):
        if a.getvalue() != b.getvalue():
            raise self.failureException(msg)

    def test_environ(self):
        event = {
            'httpMethod': 'TEST',
            'path': '/test',
            'queryStringParameters': {
                'test': '✓',
            },
            'body': u'test',
            'headers': {
                'X-test-suite': 'testing',
                'Content-type': 'text/plain',
                'Host': 'test',
                'X-forwarded-for': 'first, second',
                'X-forwarded-proto': 'https',
                'X-forwarded-port': '12345',
            },
        }
        context = object()
        expected = {
            'REQUEST_METHOD': event['httpMethod'],
            'SCRIPT_NAME': '',
            'PATH_INFO': event['path'],
            'QUERY_STRING': urlencode(event['queryStringParameters']),
            'CONTENT_LENGTH': str(len(event['body'])),
            'HTTP': 'on',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.input': BytesIO(event['body'].encode('utf-8')),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'CONTENT_TYPE': event['headers']['Content-type'],
            'HTTP_CONTENT_TYPE': event['headers']['Content-type'],
            'SERVER_NAME': event['headers']['Host'],
            'HTTP_HOST': event['headers']['Host'],
            'REMOTE_ADDR': event['headers']['X-forwarded-for'].split(', ')[0],
            'HTTP_X_FORWARDED_FOR': event['headers']['X-forwarded-for'],
            'wsgi.url_scheme': event['headers']['X-forwarded-proto'],
            'HTTP_X_FORWARDED_PROTO': event['headers']['X-forwarded-proto'],
            'SERVER_PORT': event['headers']['X-forwarded-port'],
            'HTTP_X_FORWARDED_PORT': event['headers']['X-forwarded-port'],
            'HTTP_X_TEST_SUITE': event['headers']['X-test-suite'],
            'awsgi.event': event,
            'awsgi.context': context
        }
        result = awsgi.environ(event, context)
        self.addTypeEqualityFunc(BytesIO, self.compareStringIOContents)
        for k, v in result.items():
            self.assertEqual(v, expected[k])

    def test_response_base64_content_type(self):
        event = {
            "path": "/image.png",
            "httpMethod": "GET",
            "headers": {
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "X-Forwarded-For": "first, second",
                "X-Forwarded-Port": "12345",
                "X-Forwarded-Proto": "https",
            },
        }
        context = object()
        sr = awsgi.StartResponse(
            base64_content_types={"image/png"}
        )
        sr("200 OK", [("Content-Type", "image/png")])
        output = BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8")

        result = sr.response(output)
        self.assertTrue(result["isBase64Encoded"])
        self.assertEqual(result["body"], 'iVBORw0KGgoAAAANSUhEUgAAAMg=')

    def test_impl_selection_elb(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-2:0123456789:targetgroup/spam/eggs"
                }
            },
            "httpMethod": "GET",
            "path": "/",
            "multiValueQueryStringParameters": {},
            "multiValueHeaders": {
                "user-agent": [
                    "ELB-HealthChecker/2.0"
                ]
            },
            "body": "",
            "isBase64Encoded": False
        }
        context = object()
        environ, StartResponse = awsgi.select_impl(event, context)
        self.assertIs(environ, awsgi.environ)
        self.assertIs(StartResponse, awsgi.StartResponse_ELB)

    def test_impl_selection_gw(self):
        # From https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html?shortFooter=true
        event = {
          "path": "/test/hello",
          "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, lzma, sdch, br",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "wt6mne2s9k.execute-api.us-west-2.amazonaws.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36 OPR/39.0.2256.48",
            "Via": "1.1 fb7cca60f0ecd82ce07790c9c5eef16c.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "nBsWBOrSHMgnaROZJK1wGCZ9PcRcSpq_oSXZNQwQ10OTZL4cimZo3g==",
            "X-Forwarded-For": "192.168.100.1, 192.168.1.1",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
          },
          "pathParameters": {
            "proxy": "hello"
          },
          "requestContext": {
            "accountId": "123456789012",
            "resourceId": "us4z18",
            "stage": "test",
            "requestId": "41b45ea3-70b5-11e6-b7bd-69b5aaebc7d9",
            "identity": {
              "cognitoIdentityPoolId": "",
              "accountId": "",
              "cognitoIdentityId": "",
              "caller": "",
              "apiKey": "",
              "sourceIp": "192.168.100.1",
              "cognitoAuthenticationType": "",
              "cognitoAuthenticationProvider": "",
              "userArn": "",
              "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36 OPR/39.0.2256.48",
              "user": ""
            },
            "resourcePath": "/{proxy+}",
            "httpMethod": "GET",
            "apiId": "wt6mne2s9k"
          },
          "resource": "/{proxy+}",
          "httpMethod": "GET",
          "queryStringParameters": {
            "name": "me"
          },
          "stageVariables": {
            "stageVarName": "stageVarValue"
          }
        }
        context = object()
        environ, StartResponse = awsgi.select_impl(event, context)
        self.assertIs(environ, awsgi.environ)
        self.assertIs(StartResponse, awsgi.StartResponse_GW)
