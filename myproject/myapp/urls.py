from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/<str:commodity>/', views.home, name = 'home'),
    path('commodity_selection/', views.commodity_selection, name = 'commodity_selection'),
    path('country_selection/', views.country_selection, name = 'country_selection'),
    path('country_selection/<str:country>/', views.country_selection, name = 'country_selection'),
    path('country_commodity_selection/', views.country_commodity_selection, name = 'country_commodity_selection'),
    path('country_commodity_selection/<str:country>', views.country_commodity_selection, name = 'country_commodity_selection'),
    path('generate_video_country/', views.running_bar_chart_country, name = 'generate_chart'),
    path('generate_video_country/<str:country>', views.running_bar_chart_country, name = 'generate_chart'),
    path('generate_video_home/', views.running_bar_chart_home, name = 'generate_video'),
    path('generate_video_home/<str:commodity>', views.running_bar_chart_home, name = 'generate_video'),
]