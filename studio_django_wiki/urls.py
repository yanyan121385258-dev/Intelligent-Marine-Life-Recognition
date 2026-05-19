from django.urls import path, include

app_name = 'studio_django_wiki'

urlpatterns = [
    # 知识管理相关API
    path('', include('studio_django_wiki.urls.wiki_urls')),
]