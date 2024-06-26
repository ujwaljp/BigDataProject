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
    path('trend_analysis/', views.trend_analysis, name = 'trend_analysis'),
    path('trend_analysis/<str:sector>', views.trend_analysis, name = 'trend_analysis'),
    path('commodity_country_selection/', views.commodity_country_selection, name = 'commodity_country_selection'),
    path('commodity_country_selection/<str:commodity>', views.commodity_country_selection, name = 'commodity_country_selection'),
]