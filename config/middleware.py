"""Small limits and response headers shared by the page and JSON API."""

import json

from starlette.responses import PlainTextResponse


class PublicAppMiddleware:
    max_body = 16 * 1024

    def __init__(self, app, *, trust_cloudflare=False, production=False):
        self.app = app
        self.trust_cloudflare = trust_cloudflare
        self.production = production

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        headers = dict(scope['headers'])
        # Enable only behind the existing Cloudflare -> nginx -> Next.js chain.
        # The container has no published ports and an internal-only network. Cloudflare
        # supplies this header; nginx currently overwrites X-Forwarded-Proto.
        if self.trust_cloudflare:
            try:
                scheme = json.loads(headers.get(b'cf-visitor', b'{}')).get('scheme')
            except (ValueError, AttributeError, UnicodeDecodeError):
                scheme = None
            scope = dict(scope, scheme='https' if scheme == 'https' else 'http')
            # Next.js changes Host to the backend IP and supplies the original
            # host itself. Restore it before TrustedHostMiddleware validates it.
            if b'x-forwarded-host' in headers:
                scope['headers'] = [
                    (key, value) for key, value in scope['headers'] if key != b'host'
                ] + [(b'host', headers[b'x-forwarded-host'])]

        async def secure_send(message):
            if message['type'] == 'http.response.start':
                message['headers'] = list(message.get('headers', []))
                existing = {key.lower() for key, _ in message['headers']}
                extra = {
                    b'x-content-type-options': b'nosniff',
                    b'x-frame-options': b'DENY',
                    b'referrer-policy': b'no-referrer',
                    b'cache-control': b'no-store',
                    b'content-security-policy': (
                        b"default-src 'none'; script-src 'self'; "
                        b"style-src 'self' 'unsafe-inline'; connect-src 'self'; "
                        b"base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
                    ),
                }
                if self.production and scope['scheme'] == 'https':
                    extra[b'strict-transport-security'] = b'max-age=3600'
                message['headers'].extend((key, value) for key, value in extra.items() if key not in existing)
            await send(message)

        # Read at most 16 KiB, including chunked bodies, before JSON parsing.
        body = bytearray()
        while True:
            event = await receive()
            if event['type'] == 'http.disconnect':
                return
            body.extend(event.get('body', b''))
            if len(body) > self.max_body:
                return await PlainTextResponse('Request too large', status_code=413)(scope, receive, secure_send)
            if not event.get('more_body', False):
                break

        delivered = False

        async def limited_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()

        await self.app(scope, limited_receive, secure_send)
