from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html', {
        'api_url': settings.APP_BASE_PATH + '/api/links',
        'app_js_url': settings.APP_BASE_PATH + '/app.js',
    })


def app_js(request):
    return HttpResponse((settings.BASE_DIR / 'static/app.js').read_bytes(), content_type='text/javascript')
