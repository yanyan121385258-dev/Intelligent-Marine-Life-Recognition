from django.urls import path, include
from views import *

urlpatterns = [
    path('test/', test, name='test'),
]