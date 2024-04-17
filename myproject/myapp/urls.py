from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/<str:commodity>/', views.home, name = 'home'),
    path('commodity_selection', views.commodity_selection, name = 'commodity_selection')
]