from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = 'blogs'

urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('category/<str:category>/', views.CategoryView.as_view(), name='category'),
        path('detail/<int:pk>/', views.BlogDetailView.as_view(), name='detail'),
        path('private_index/', views.PrivateIndexView.as_view(), name='private_index'),
        path('private_index/private_detail/<int:pk>/',
                    views.PrivateDetailView.as_view(), name='private_detail'),
        path('new_blog/', views.BlogFormView.as_view(), name='new_blog'),
        path('edit_blog/<int:pk>/', views.EditBlogFormView.as_view(), name='edit_blog'),
        path('release/<pk>/', views.release, name='release'),
        path('private/<pk>/', views.private, name='private'),
        path('category_graph/', views.CategoryGraphView.as_view(), name='category_graph'),
]

