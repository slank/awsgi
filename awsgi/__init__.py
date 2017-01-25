import base64
from io import BytesIO
import sys
try:
    # Python 3
    from urllib.parse import urlencode
except:
    # Python 2
    from urllib import urlencode


def response(app, event, context):
    sr = StartResponse()
    output = app(environ(event, context), sr)
    return sr.response(output)


class StartResponse:
    def __init__(self):
        self.status = 500
        self.headers = []
        self.body = BytesIO()

    def __call__(self, status, headers, exc_info=None):
        self.status = status.split()[0]
        self.headers[:] = headers
        return self.body.write

    def response(self, output):
        resp = {
            'statusCode': str(self.status),
            'headers': dict(self.headers),
            'body': self.body.getvalue(),
        }

        if output:
            body = bytearray(resp['body'])
            [body.extend(chunk) for chunk in output]

            resp['body'] = base64.b64encode(body)
            resp['isBase64Encoded'] = True

        return resp


def environ(event, context):
    if event.get('isBase64Encoded', False) and event.has_key('body'):
        event['body'] = base64.b64decode(event['body'])

    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': urlencode(event['queryStringParameters'] or {}),
        'REMOTE_ADDR': '127.0.0.1',
        'CONTENT_LENGTH': str(len(event.get('body', '') or '')),
        'HTTP': 'on',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.input': BytesIO(event.get('body')),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    headers = event.get('headers') or {}
    for k, v in headers.items():
        k = k.title()
        if k == 'Content-Type':
            environ['CONTENT_TYPE'] = v
        if k == 'Host':
            environ['SERVER_NAME'] = v
        if k == 'X-Forwarded-For':
            environ['REMOTE_ADDR'] = v.split(', ')[0]
        if k == 'X-Forwarded-Proto':
            environ['wsgi.url_scheme'] = v
        if k == 'X-Forwarded-Port':
            environ['SERVER_PORT'] = v
        environ['HTTP_' + k.upper().replace('-', '_')] = v

    return environ
