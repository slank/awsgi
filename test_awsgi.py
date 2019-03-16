# -*- coding: utf-8 -*-
from io import StringIO
import sys
import unittest
import awsgi
from awsgi import urlencode


class TestAwsgi(unittest.TestCase):
    def compareStringIOContents(self, a, b, msg=None):
        a_loc = a.tell()
        b_loc = b.tell()
        a.seek(0)
        b.seek(0)
        if a.read() != b.read():
            raise self.failureException(msg)
        a.seek(a_loc)
        b.seek(b_loc)

    def verify_environ(self, expected, result):
        self.addTypeEqualityFunc(StringIO, self.compareStringIOContents)
        self.assertEqual(set(result.keys()), set(expected.keys()))
        for k, v in result.items():
            self.assertEqual(v, expected[k])

    def test_environ(self):
        """Tests a request with no authorizer context.  The REMOTE_USER should be omitted in this case"""
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
            }
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
            'wsgi.input': StringIO(event['body']),
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
        self.verify_environ(expected, result)

    def test_environ_with_authorizer(self):
        """Tests a request with an authorizer context.  The REMOTE_USER should be included"""
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
            'requestContext': {
                'authorizer': {'principalId': 'user1'}
            }
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
            'wsgi.input': StringIO(event['body']),
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
            'awsgi.context': context,
            'REMOTE_USER': 'user1'
        }
        result = awsgi.environ(event, context)
        self.verify_environ(expected, result)
