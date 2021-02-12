from django.urls import path
from . import views

app_name = 'stormstats'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('roster/', views.RosterView.as_view(), name='roster'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('skaterstats/', views.SkaterStatsView.as_view(), name='skaterstats'),
    path('goaliestats/', views.GoalieStatsView.as_view(), name='goaliestats'),
    path('skatergamestats/bygame/', views.SkaterGameStatsByGameView.as_view(), name='skatergamestatsbygame'),
    path('skatergamestats/byplayer/', views.SkaterGameStatsByPlayerView.as_view(), name='skatergamestatsbyplayer'),
    path('goaliegamestats/', views.GoalieGameStatsView.as_view(), name='goaliegamestats'),
]