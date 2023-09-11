from django.core.handlers.wsgi import WSGIRequest


def _saveFile(file, filepath):
    with open(filepath, mode='wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return filepath


def getFile(request: WSGIRequest, file_key, path='', filename=None, if_save_file=True):
    file = request.FILES.get(file_key)
    filepath = f'{path}/{filename if filename else file.name}'
    if if_save_file:
        return _saveFile(file, filepath)
    else:
        return file


def getFiles(request: WSGIRequest, files_key, path='', filename_qz=None, if_save_file=True):
    files = request.FILES.getlist(files_key)
    res = list()
    for file in files:
        filepath = f'{path}/{filename_qz if filename_qz else ""}{file.name}'
        if if_save_file:
            with open(filepath, mode='wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            res.append(filepath)
        else:
            res.append(file)


def getIp(request):
    #nginx反向代理设置proxy_set_header x-forwarded-for  $remote_addr; 即可访问真实ip地址
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip
