from django.contrib.auth.models import Permission
from django.shortcuts import render

from studio_django_auth.utils.decorators import no_login_required


@no_login_required
def index(request):
    """
    系统首页视图
    展示系统的基础介绍和功能特性
    """
    return render(request, 'index.html')