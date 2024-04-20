from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/<str:commodity>/', views.home, name = 'home'),
    path('commodity_selection/', views.commodity_selection, name = 'commodity_selection'),
    path('country_selection/', views.country_selection, name = 'country_selection'),
    path('country_selection/<str:country>/', views.country_selection, name = 'country_selection'),
]