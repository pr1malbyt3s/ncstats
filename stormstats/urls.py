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
    path('skatergamestats/', views.SkaterGameStatsView.as_view(), name='skatergamestats'),
    path('goaliegamestats/', views.GoalieGameStatsView.as_view(), name='goaliegamestats'),
]