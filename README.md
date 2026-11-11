# Easy Hyperlink

Create a named hyperlink, preview it, and copy it as rich text in supported applications. Django serves the page and FastAPI validates HTTP/HTTPS addresses. Links are not saved, and the server does not visit the supplied address.

**Live app:** https://oscareustate.com/easy-hyperlink

**Project page:** https://oscareustate.com/projects/easy-hyperlink

The page includes a before/after example, a quick usage guide, and [formatted paste guidance](docs/clipboard-compatibility.md) for email and document editors.

## Run locally

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/), then:

```sh
uv sync --frozen
uv run uvicorn config.asgi:application --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/. The page and API run together; a second API server is no longer needed. Local development defaults to debug mode and localhost hosts. Do not publish this development command.

## Production and verification

See [self-hosting](docs/self-hosting.md) for the container configuration, proxy route, update and rollback process. See [security review](docs/security-review.md) for verified controls and outstanding host checks.

```sh
uv run python -m unittest discover -s tests -v
```

Production requires `DJANGO_DEBUG=false`, a persistent random `DJANGO_SECRET_KEY`, explicit `DJANGO_ALLOWED_HOSTS`, and HTTPS. `.env.example` documents the deployment variables. Environment files, local databases, and virtual environments are excluded from Git and Docker build context.

The API validates syntax, not whether a destination is trustworthy. It rejects non-HTTP(S) URLs, URLs containing credentials, oversized requests, and empty link names. User text is inserted with `textContent`; formatted clipboard HTML is created from the resulting DOM anchor. Some applications paste only a URL. Only open destinations you trust.
