from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponse

APP_ICONS = frozenset({
    'microsoftteams', 'zoom', 'gmail', 'microsoftoutlook',
    'microsoftword', 'googledocs', 'notion',
})

def home(request):
    return render(request, 'home.html', {
        'api_url': settings.APP_BASE_PATH + '/api/links',
        'app_js_url': settings.APP_BASE_PATH + '/app.js',
        'favicon_url': settings.APP_BASE_PATH + '/favicon.svg',
        'app_icons_url': settings.APP_BASE_PATH + '/app-icons/',
    })


def app_js(request):
    return HttpResponse((settings.BASE_DIR / 'static/app.js').read_bytes(), content_type='text/javascript')


def favicon(request):
    return HttpResponse((settings.BASE_DIR / 'static/favicon.svg').read_bytes(), content_type='image/svg+xml')


def app_icon(request, name):
    if name not in APP_ICONS:
        raise Http404
    return HttpResponse(
        (settings.BASE_DIR / 'static/app-icons' / (name + '.svg')).read_bytes(),
        content_type='image/svg+xml',
    )
