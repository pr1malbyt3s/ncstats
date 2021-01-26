from django.urls import path
from . import views

app_name = 'stormstats'
urlpatterns = [
    path('', views.player_list, name='index'),
]