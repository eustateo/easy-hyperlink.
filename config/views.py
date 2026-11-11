from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html', {
        'api_url': settings.APP_BASE_PATH + '/api/links',
        'app_js_url': settings.APP_BASE_PATH + '/app.js',
        'favicon_url': settings.APP_BASE_PATH + '/favicon.svg',
    })


def app_js(request):
    return HttpResponse((settings.BASE_DIR / 'static/app.js').read_bytes(), content_type='text/javascript')


def favicon(request):
    return HttpResponse((settings.BASE_DIR / 'static/favicon.svg').read_bytes(), content_type='image/svg+xml')
