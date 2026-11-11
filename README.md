# Easy Hyperlink

A small learning project that uses Django to serve a page and FastAPI to validate link names and web addresses. Create a link, copy it as rich text in supported applications, or copy its address using the browser's context menu. Links are not saved.

## Run locally

Install Python 3.12 or newer and [uv](https://docs.astral.sh/uv/). From this directory, install dependencies:

```powershell
uv sync
```

In one terminal run Django:

```powershell
uv run python manage.py runserver 127.0.0.1:8000
```

In another terminal run the API:

```powershell
uv run uvicorn api:app --reload --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8000/. Both servers must run for the form to work. Stop either server with Ctrl+C.

## Security and development

This is a local learning project, not a production deployment configuration. Django debug mode is enabled, and the browser and CORS settings are tied to localhost. Do not expose the development servers to the internet. For deployment, configure a persistent secret key through `DJANGO_SECRET_KEY`, disable debug mode, configure allowed hosts and HTTPS, and follow Django's deployment checklist. Without the environment variable, a new random key is generated on each startup, invalidating signed sessions when the server restarts.

The local SQLite database, environment files, and virtual environment are excluded from Git. The API checks URL syntax but cannot establish whether a destination is trustworthy. Rich-text paste depends on the destination application; some apps paste only the URL.
