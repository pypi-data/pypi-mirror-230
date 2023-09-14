import json
from functools import wraps
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse


class HttpResponseUnAuth(HttpResponse):
    status_code = 401


def check_login(view_func):

    @wraps(view_func)
    def wrapper_view(*args, **kwargs):
        should_auth = getattr(settings, 'MADMIN', {}).get('upload_auth', False)
        if should_auth:
            request = args[0] if len(args) else kwargs.get('request')
            user = request.user if request else None
            if not user or not user.is_authenticated:
                return HttpResponseUnAuth()
        return view_func(*args, **kwargs)

    return wrapper_view


def get_file_path(hash, name):
    ext_parts = name.rsplit('.', 1)
    ext = ('.' + ext_parts[1]) if len(ext_parts) > 1 else ''
    file_path = 'madmin/{}{}'.format(hash, ext)
    return file_path


def get_request_data(request: HttpRequest):
    data = request.POST
    try:
        data = json.loads(request.body)
    except Exception:
        pass
    return data or {}


@check_login
@csrf_exempt
@require_POST
def upload(request: HttpRequest):
    data = get_request_data(request)
    hash = data.get('hash')
    file = request.FILES.get('file')
    if not bool(hash):
        return HttpResponseBadRequest('缺少输入参数hash')
    if not bool(file):
        return HttpResponseBadRequest('缺少输入参数file')

    file_path = get_file_path(hash, file.name)

    if not default_storage.exists(file_path):
        default_storage.save(file_path, file)

    file_url = default_storage.url(file_path)
    return JsonResponse({'file_url': file_url})


@check_login
@csrf_exempt
@require_POST
def check_upload(request: HttpRequest):
    data = get_request_data(request)
    hash = data.get('hash')
    name = data.get('name')
    if not bool(hash):
        return HttpResponseBadRequest('缺少输入参数hash')
    if not bool(name):
        return HttpResponseBadRequest('缺少输入参数name')

    file_path = get_file_path(hash, name)
    file_url = ''
    upload_url = ''
    if default_storage.exists(file_path):
        file_url = default_storage.url(file_path)
    else:
        upload_url = reverse(upload)
    return JsonResponse({'file_url': file_url, 'upload_url': upload_url})
