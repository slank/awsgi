from io import StringIO, BytesIO
from base64 import b64encode, b64decode
import sys
try:
    # Python 3
    from urllib.parse import urlencode

    # Convert bytes to str, if required
    def convert_str(s):
        return s.decode('utf-8') if isinstance(s, bytes) else s
except:
    # Python 2
    from urllib import urlencode

    # No conversion required
    def convert_str(s):
        return s


def convert_b46(s):
    return b64encode(s).decode('ascii')


def response(app, event, context, base64_content_types=None):
    sr = StartResponse(base64_content_types=base64_content_types)
    output = app(environ(event, context), sr)
    return sr.response(output)


class StartResponse:
    def __init__(self, base64_content_types=None):
        '''
        Args:
            base64_content_types (set): Set of HTTP Content-Types which should
            return a base64 encoded body. Enables returning binary content from
            API Gateway.
        '''
        self.status = 500
        self.headers = []
        self.body = StringIO()
        self.base64_content_types = set(base64_content_types or []) or set()

    def __call__(self, status, headers, exc_info=None):
        self.status = status.split()[0]
        self.headers[:] = headers
        return self.body.write

    def response(self, output):
        headers = dict(self.headers)
        is_b64 = headers.get('Content-Type') in self.base64_content_types

        if is_b64:
            converted_output = ''.join(map(convert_b46, output))
        else:
            converted_output = ''.join(map(convert_str, output))

        return {
            'isBase64Encoded': is_b64,
            'statusCode': str(self.status),
            'headers': headers,
            'body': self.body.getvalue() + converted_output,
        }


def environ(event, context):
    if event.get('isBase64Encoded', False):
        body_buffer = b64decode(event.get('body', '') or '')
        body_file = BytesIO(body_buffer)
    else:
        # FIXME: Flag the encoding in the headers
        body_buffer = event.get('body', '') or ''
        body_file = BytesIO(body_buffer.encode('utf-8'))

    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'SERVER_NAME': '',
        'SERVER_PORT': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': urlencode(event['queryStringParameters'] or {}),
        'REMOTE_ADDR': '127.0.0.1',
        'CONTENT_LENGTH': str(len(body_buffer)),
        'HTTP': 'on',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.input': body_file,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'awsgi.event': event,
        'awsgi.context': context,
    }
    headers = event.get('headers', {})
    for k, v in headers.items():
        k = k.upper().replace('-', '_')

        if k == 'CONTENT_TYPE':
            environ['CONTENT_TYPE'] = v
        elif k == 'HOST':
            environ['SERVER_NAME'] = v
        elif k == 'X_FORWARDED_FOR':
            environ['REMOTE_ADDR'] = v.split(', ')[0]
        elif k == 'X_FORWARDED_PROTO':
            environ['wsgi.url_scheme'] = v
        elif k == 'X_FORWARDED_PORT':
            environ['SERVER_PORT'] = v

        environ['HTTP_' + k] = v

    return environ
