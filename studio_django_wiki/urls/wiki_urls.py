from django.urls import path
from ..views import (
    # 知识分类管理
    wiki_category_list, wiki_category_tree, wiki_category_create,
    wiki_category_detail, wiki_category_update, wiki_category_delete,
    # 知识文章管理
    wiki_article_list, wiki_article_create, wiki_article_detail,
    wiki_article_update, wiki_article_delete, wiki_article_publish,
    wiki_article_archive, wiki_article_import
)

urlpatterns = [
    # ==================== 知识分类管理 ====================
    path('categories/', wiki_category_list, name='wiki_category_list'),
    path('categories/tree/', wiki_category_tree, name='wiki_category_tree'),
    path('categories/create/', wiki_category_create, name='wiki_category_create'),
    path('categories/<str:category_id>/', wiki_category_detail, name='wiki_category_detail'),
    path('categories/<str:category_id>/update/', wiki_category_update, name='wiki_category_update'),
    path('categories/<str:category_id>/delete/', wiki_category_delete, name='wiki_category_delete'),
    
    # ==================== 知识文章管理 ====================
    path('articles/', wiki_article_list, name='wiki_article_list'),
    path('articles/create/', wiki_article_create, name='wiki_article_create'),
    path('articles/import/', wiki_article_import, name='wiki_article_import'),
    path('articles/<str:article_id>/', wiki_article_detail, name='wiki_article_detail'),
    path('articles/<str:article_id>/update/', wiki_article_update, name='wiki_article_update'),
    path('articles/<str:article_id>/delete/', wiki_article_delete, name='wiki_article_delete'),
    path('articles/<str:article_id>/publish/', wiki_article_publish, name='wiki_article_publish'),
    path('articles/<str:article_id>/archive/', wiki_article_archive, name='wiki_article_archive'),
]