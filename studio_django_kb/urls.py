from django.urls import path
from . import views

urlpatterns = [
    path('items/create/', views.kb_item_create, name='kb_item_create'),
    path('items/list/', views.kb_item_list, name='kb_item_list'),
    path('search/', views.kb_search, name='kb_search'),
    path('qa/', views.kb_qa, name='kb_qa'),
    path('graph/entities/', views.kb_entity_list_create, name='kb_entity_list_create'),
    path('graph/entities/<int:pk>/', views.kb_entity_update_delete, name='kb_entity_update_delete'),
    path('graph/relations/', views.kb_relation_list_create, name='kb_relation_list_create'),
    path('graph/relations/<int:pk>/', views.kb_relation_delete, name='kb_relation_delete'),
    path('graph/extract/', views.kb_graph_extract, name='kb_graph_extract'),
    path('graph/extract/batch/', views.kb_graph_extract_batch, name='kb_graph_extract_batch'),
]
