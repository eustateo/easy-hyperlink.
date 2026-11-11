"""Security and routing checks against the real composed ASGI application."""
import asyncio
import json
import os
import secrets
import unittest

os.environ.update(
    DJANGO_DEBUG='false', DJANGO_SECRET_KEY=secrets.token_urlsafe(64),
    DJANGO_ALLOWED_HOSTS='oscareustate.com,127.0.0.1',
    APP_BASE_PATH='/easy-hyperlink', TRUST_CLOUDFLARE='true',
)
from config.asgi import application


async def request(path, *, method='GET', body=b'', host='oscareustate.com', scheme='https', chunks=None):
    events = []
    chunks = list(chunks if chunks is not None else [body])
    scope = {
        'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
        'method': method, 'scheme': 'http', 'path': path, 'raw_path': path.encode(),
        'root_path': '', 'query_string': b'', 'server': ('127.0.0.1', 8000),
        'client': ('127.0.0.1', 12345),
        'headers': [(b'host', host.encode()), (b'content-type', b'application/json'),
                    (b'cf-visitor', json.dumps({'scheme': scheme}).encode())],
    }

    async def receive():
        if chunks:
            data = chunks.pop(0)
            return {'type': 'http.request', 'body': data, 'more_body': bool(chunks)}
        await asyncio.Event().wait()

    async def send(message):
        events.append(message)

    await asyncio.wait_for(application(scope, receive, send), timeout=5)
    start = next(event for event in events if event['type'] == 'http.response.start')
    content = b''.join(event.get('body', b'') for event in events if event['type'] == 'http.response.body')
    return start['status'], dict(start['headers']), content


class PublicAppTests(unittest.TestCase):
    def call(self, *args, **kwargs):
        return asyncio.run(request(*args, **kwargs))

    def test_page_and_javascript_use_same_origin(self):
        status, headers, body = self.call('/easy-hyperlink/')
        self.assertEqual(status, 200)
        self.assertIn(b'data-api-url="/easy-hyperlink/api/links"', body)
        self.assertNotIn(b'127.0.0.1', body)
        self.assertIn(b"script-src 'self';", headers[b'content-security-policy'])
        self.assertEqual(self.call('/easy-hyperlink/app.js')[0], 200)

    def test_valid_link_and_untrusted_markup_stay_data(self):
        status, headers, body = self.call('/easy-hyperlink/api/links', method='POST',
            body=json.dumps({'name': '  <img src=x onerror=alert(1)>  ', 'url': 'https://example.com'}).encode())
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['name'], '<img src=x onerror=alert(1)>')
        self.assertEqual(json.loads(body)['url'], 'https://example.com/')
        self.assertIn(b'application/json', headers[b'content-type'])
        self.assertEqual(headers[b'cache-control'], b'no-store')

    def test_invalid_and_credential_urls_rejected(self):
        for url in ['javascript:alert(1)', 'file:///etc/passwd', 'ftp://example.com',
                    'http://user:pass@example.com', 'not-a-url', 'https://example.com/'+'x'*2048]:
            with self.subTest(url=url[:60]):
                status, _, _ = self.call('/easy-hyperlink/api/links', method='POST',
                    body=json.dumps({'name': 'Test', 'url': url}).encode())
                self.assertEqual(status, 422)

    def test_empty_names_and_malformed_json_rejected(self):
        for body in [b'{', b'{"name":"   ","url":"https://example.com"}']:
            self.assertEqual(self.call('/easy-hyperlink/api/links', method='POST', body=body)[0], 422)

    def test_host_header_and_https(self):
        self.assertEqual(self.call('/easy-hyperlink/', host='evil.example')[0], 400)
        status, headers, _ = self.call('/easy-hyperlink/', scheme='http')
        self.assertEqual(status, 307)
        self.assertEqual(headers[b'location'], b'https://oscareustate.com/easy-hyperlink/')

    def test_chunked_payload_limit(self):
        self.assertEqual(self.call('/easy-hyperlink/api/links', method='POST',
            chunks=[b'x'*9000, b'x'*9000])[0], 413)

    def test_no_admin_or_api_schema(self):
        for path in ['/easy-hyperlink/admin/', '/easy-hyperlink/api/docs',
                     '/easy-hyperlink/api/openapi.json', '/easy-hyperlink/.env',
                     '/easy-hyperlink/.git/config']:
            with self.subTest(path=path):
                self.assertEqual(self.call(path)[0], 404)


if __name__ == '__main__':
    unittest.main()
