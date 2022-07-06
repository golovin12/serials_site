from django.shortcuts import render

# Обработчик ошибок
def m304(request):
    return render(request, 'errors/304.html')


def m400(request, exeption):
    return render(request, 'errors/400.html', {'exeption': exeption})


def m403(request, exeption):
    return render(request, 'errors/403.html', {'exeption': exeption})


def m404(request, exeption):
    return render(request, 'errors/404.html', {'exeption': exeption})


def m405(request):
    return render(request, 'errors/405.html')


def m410(request):
    return render(request, 'errors/410.html')


def m500(request):
    return render(request, 'errors/500.html')