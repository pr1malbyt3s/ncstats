from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from .models import Game, GoalieGameStats, GoalieOverallStats, Player, SkaterGameStats, SkaterOverallStats
import json

class HomeView(generic.TemplateView):
    template_name = 'stormstats/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Home"
        context['home_activate'] = 'active'
        dataset = Player.objects.values('name', 'age').order_by('age')
        names = list()
        ages = list()
        for entry in dataset:
            names.append(entry['name'])
            ages.append(entry['age'])
        ages_series = {
            'name': 'Ages',
            'data': ages,
            'color': 'red'
        }
        chart = {
            'chart': {'type':'lollipop', 'borderColor':'black', 'borderWidth':2},
            'plotOptions': {'lollipop': {'connectorColor':'black'}},
            'credits': {'enabled':False},
            'title': {'text':'Roster Ages'},
            'xAxis': {'title': {'text':'Player'}, 'categories':names},
            'yAxis': {'title': {'text':'Age'}},
            'series': [ages_series]
        }
        context['chart'] = json.dumps(chart)
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
        dataset = Player.objects.values('name', 'weight', 'height').order_by('name')
        data_list = list()
        for entry in dataset:
            data_list.append({'name':entry['name'], 'data':[[entry['weight'], entry['height']]]})
        chart = {
            'chart': {'type':'scatter', 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Roster Weight vs. Height'},
            'xAxis': {'title': {'text':'Height'}},
            'yAxis': {'title': {'text':'Weight'}},
            'series': data_list
        }
        context['chart'] = json.dumps(chart)
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

class SkaterGameStatsByGameView(generic.ListView):
    model = SkaterGameStats
    template_name = 'stormstats/skatergamestats/skaterbygame.html'
    context_object_name = 'skatergamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats - By Game"
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
        try:
            g = request.POST.get('gameId')
            self.object_list = SkaterGameStats.objects.filter(game=g)
            context = self.get_context_data(**kwargs)
            recent = Game.objects.get(game_id=g)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            return render(request, self.template_name, context=context)
        except (Game.DoesNotExist, ValueError):
            recent = Game.objects.filter(played=True).latest('date')
            self.object_list = SkaterGameStats.objects.filter(game=recent.game_id)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['error_message'] = "Please select a valid game."
            return render(request, self.template_name, context=context)
        
class SkaterGameStatsByPlayerView(generic.ListView):
    model = SkaterGameStats
    template_name = 'stormstats/skatergamestats/skaterbyplayer.html'
    context_object_name = 'skatergamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats - By Player"
        context['skatergamestats_activate'] = 'active'
        context['players'] = SkaterGameStats.objects.all().distinct('player')
        return context
    def get(self, request, *args, **kwargs):
        first = SkaterGameStats.objects.order_by('player').first()
        self.object_list = SkaterGameStats.objects.filter(player=first.player)
        context = self.get_context_data(**kwargs)
        context['current_skater'] = first.player.name
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            p = request.POST.get('playerId')
            self.object_list = SkaterGameStats.objects.filter(player=p)
            context = self.get_context_data(**kwargs)
            current = Player.objects.get(player_id=p)
            context['current_skater'] = current.name
            return render(request, self.template_name, context=context)
        except (Player.DoesNotExist, ValueError):
            first = GoalieGameStats.objects.order_by('player').first()
            self.object_list = SkaterGameStats.objects.filter(player=first.player)
            context = self.get_context_data(**kwargs)
            context['current_skater'] = first.player.name
            context['error_message'] = "Please select a valid player."
            return render(request, self.template_name, context=context)

class GoalieGameStatsByGameView(generic.ListView):
    model = GoalieGameStats
    template_name = 'stormstats/goaliegamestats/goaliebygame.html'
    context_object_name = 'goaliegamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Game Stats - By Game"
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
        try:
            g = request.POST.get('gameId')
            self.object_list = GoalieGameStats.objects.filter(game=g)
            context = self.get_context_data(**kwargs)
            recent = Game.objects.get(game_id=g)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            return render(request, self.template_name, context=context)
        except (Game.DoesNotExist, ValueError):
            recent = Game.objects.filter(played=True).latest('date')
            self.object_list = GoalieGameStats.objects.filter(game=recent.game_id)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['error_message'] = "Please select a valid game."
            return render(request, self.template_name, context=context)

class GoalieGameStatsByPlayerView(generic.ListView):
    model = GoalieGameStats
    template_name = 'stormstats/goaliegamestats/goaliebyplayer.html'
    context_object_name = 'goaliegamestats'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Game Stats - By Player"
        context['goaliegamestats_activate'] = 'active'
        context['players'] = GoalieGameStats.objects.all().distinct('player')
        return context
    def get(self, request, *args, **kwargs):
        first = GoalieGameStats.objects.order_by('player').first()
        self.object_list = GoalieGameStats.objects.filter(player=first.player)
        context = self.get_context_data(**kwargs)
        context['current_goalie'] = first.player.name
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            p = request.POST.get('playerId')
            self.object_list = GoalieGameStats.objects.filter(player=p)
            context = self.get_context_data(**kwargs)
            current = Player.objects.get(player_id=p)
            context['current_goalie'] = current.name
            return render(request, self.template_name, context=context)
        except (Player.DoesNotExist, ValueError):
            first = GoalieGameStats.objects.order_by('player').first()
            self.object_list = GoalieGameStats.objects.filter(player=first.player)
            context = self.get_context_data(**kwargs)
            context['current_goalie'] = first.player.name
            context['error_message'] = "Please select a valid player."
            return render(request, self.template_name, context=context)