from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.ad_list, name='list'),
    path('post/<slug:slug>/', views.ad_detail, name='detail'),
    path('create/', views.ad_create, name='create'),
    path('post/<slug:slug>/edit/', views.ad_edit, name='edit'),
    path('post/<slug:slug>/request-deletion/', views.request_deletion, name='request_deletion'),
    path('post/<slug:slug>/delete/', views.ad_delete, name='delete'),
]
