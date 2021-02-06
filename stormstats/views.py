from django.views import generic
from .models import Game, Player, SkaterOverallStats

class HomeView(generic.TemplateView):
    template_name = 'stormstats/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Home"
        context['activate'] = 'home'
        return context

class AboutView(generic.TemplateView):
    template_name = 'stormstats/about.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - About"
        context['activate'] = 'about'
        return context

class RosterView(generic.TemplateView):
    template_name = 'stormstats/roster.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Roster"
        context['activate'] = 'roster'
        context['players'] = Player.objects.all().order_by('name')
        return context

class ScheduleView(generic.TemplateView):
    template_name = 'stormstats/schedule.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Schedule"
        context['activate'] = 'schedule'
        context['games'] = Game.objects.all().order_by('date')
        return context

class SkaterStatsView(generic.TemplateView):
    template_name = 'stormstats/skaterstats.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Stats"
        context['activate'] = 'skaterstats'
        context['skaterstats'] = SkaterOverallStats.objects.all().order_by('player__name')
        return context