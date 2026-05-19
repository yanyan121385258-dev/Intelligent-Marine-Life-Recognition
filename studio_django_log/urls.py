from django.urls import path, include

urlpatterns = [
    path('', include('studio_django_log.urls.log_urls')),
]