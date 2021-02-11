from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from .models import Game, GoalieGameStats, GoalieOverallStats, Player, SkaterGameStats, SkaterOverallStats

class HomeView(generic.TemplateView):
    template_name = 'stormstats/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Home"
        context['home_activate'] = 'active'
        dataset = Player.objects.values('name', 'age').order_by('name')
        names = list()
        ages = list()
        for entry in dataset:
            names.append(entry['name'])
            ages.append(entry['age'])
        context['names'] = names
        context['ages'] = ages
        return context

class AboutView(generic.TemplateView):
    template_name = 'stormstats/about.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - About"
        context['about_activate'] = 'active'
        return context

class RosterView(generic.ListView):
    template_name = 'stormstats/roster.html'
    context_object_name = 'players'
    queryset = Player.objects.order_by('name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Roster"
        context['roster_activate'] = 'active'
        return context   

class ScheduleView(generic.ListView):
    template_name = 'stormstats/schedule.html'
    context_object_name = 'games'
    queryset = Game.objects.order_by('date')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Schedule"
        context['schedule_activate'] = 'active'
        return context

class SkaterStatsView(generic.ListView):
    template_name = 'stormstats/skaterstats.html'
    context_object_name = 'skaterstats'
    queryset = SkaterOverallStats.objects.order_by('player__name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Stats"
        context['skaterstats_activate'] = 'active'
        return context

class GoalieStatsView(generic.ListView):
    template_name = 'stormstats/goaliestats.html'
    context_object_name = 'goaliestats'
    queryset = GoalieOverallStats.objects.order_by('player__name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Stats"
        context['goaliestats_activate'] = 'active'
        return context

class SkaterGameStatsView(generic.ListView):
    model = SkaterGameStats
    template_name = 'stormstats/skatergamestats.html'
    context_object_name = 'skatergamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats"
        context['skatergamestats_activate'] = 'active'
        context['games'] = Game.objects.filter(played=True)
        return context
    def get(self, request, *args, **kwargs):
        recent = Game.objects.filter(played=True).latest('date')
        self.object_list = SkaterGameStats.objects.filter(game=recent.game_id)
        context = self.get_context_data(**kwargs)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        g = request.POST.get('gameId')
        self.object_list = SkaterGameStats.objects.filter(game=g)
        context = self.get_context_data(**kwargs)
        recent = Game.objects.get(game_id=g)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        return render(request, self.template_name, context=context)

class GoalieGameStatsView(generic.ListView):
    model = GoalieGameStats
    template_name = 'stormstats/goaliegamestats.html'
    context_object_name = 'goaliegamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Game Stats"
        context['goaliegamestats_activate'] = 'active'
        context['games'] = Game.objects.filter(played=True)
        return context
    def get(self, request, *args, **kwargs):
        recent = Game.objects.filter(played=True).latest('date')
        self.object_list = GoalieGameStats.objects.filter(game=recent.game_id)
        context = self.get_context_data(**kwargs)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        g = request.POST.get('gameId')
        self.object_list = GoalieGameStats.objects.filter(game=g)
        context = self.get_context_data(**kwargs)
        recent = Game.objects.get(game_id=g)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        return render(request, self.template_name, context=context)