from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from .models import Game, GoalieGameStats, GoalieOverallStats, Player, SkaterGameStats, SkaterOverallStats
import simplejson as json

class HomeView(generic.TemplateView):
    template_name = 'stormstats/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Home"
        context['home_activate'] = 'active'
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
    queryset = Player.objects.all()
    dataset = queryset.values().order_by('name')
    def age_chart_gen(self):
        names = list()
        ages = list()
        for entry in self.dataset:
            names.append(entry['name'])
            ages.append(entry['age'])
        ages_series = {
            'name': 'Ages',
            'data': ages,
            'color': 'red'
        }
        age_chart = {
            'chart': {'type':'lollipop', 'borderColor':'black', 'borderWidth':2},
            'plotOptions': {'lollipop': {'connectorColor':'black'}},
            'credits': {'enabled':False},
            'title': {'text':'Roster Ages'},
            'xAxis': {'title': {'text':'Player'}, 'categories':names},
            'yAxis': {'title': {'text':'Age'}},
            'series': [ages_series]
        }
        return age_chart
    def hw_chart_gen(self):
        hw_data = list()
        for entry in self.dataset:
            hw_data.append({'name':entry['name'], 'data':[[entry['weight'], entry['height']]]})
        hw_chart = {
            'chart': {'type':'scatter', 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Roster Weight vs. Height'},
            'xAxis': {'title': {'text':'Height'}},
            'yAxis': {'title': {'text':'Weight'}},
            'series': hw_data
        }
        return hw_chart
    def map_chart_gen(self):
        map_data = list()
        map_data.append({'name':'Birtplace Map', 'borderColor':'#A0A0A0', 'nullColor':'#ffffff', 'showInLegend':False})
        for entry in self.dataset:
            map_data.append({'type':'mappoint', 'name':entry['name'], 'data':[{'name':entry['birthplace'], 'lat':entry['bp_lat'], 'lon':entry['bp_long']}]})
        map_chart = {
            'chart': {'map':'custom/world', 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Birthplaces'},
            'mapNavigation': {'enabled':True},
            'tooltip': {'headerFormat': '', 'pointFormat':'<b>{series.name}</b><br>Lat: {point.lat}, Lon: {point.lon}'},
            'series': map_data
        }
        return map_chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Roster"
        context['roster_activate'] = 'active'
        age_chart = self.age_chart_gen()
        context['age_chart'] = json.dumps(age_chart)
        hw_chart = self.hw_chart_gen()
        context['hw_chart'] = json.dumps(hw_chart)
        map_chart = self.map_chart_gen()
        context['map_chart'] = json.dumps(map_chart)
        return context

class ScheduleView(generic.ListView):
    template_name = 'stormstats/schedule.html'
    context_object_name = 'games'
    def get_queryset(self):
        queryset = {
            'played_games': Game.objects.all().filter(played=True).order_by('date'),
            'remaining_games': Game.objects.all().filter(played=False).order_by('date')
        }
        return queryset
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
    template_name = 'stormstats/skatergamestats/skaterbyplayer.html'
    context_object_name = 'skatergamestats'
    object_list = SkaterGameStats.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats - By Player"
        context['skatergamestats_activate'] = 'active'
        context['players'] = SkaterGameStats.objects.all().distinct('player')
        return context
    def points_chart_gen(self, p):
        dataset = self.object_list.filter(player=p).order_by('game__date')
        dates = list()
        goal_data = list()
        assist_data = list()
        point_data = list()
        goals = 0
        assists = 0
        points = 0
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            goals += entry.goals
            assists += entry.assists
            points += entry.points
            goal_data.append(goals)
            assist_data.append(assists)
            point_data.append(points)
        goals_series = {
            'name': 'Goals',
            'color': 'red',
            'data': goal_data
        }
        assists_series = {
            'name': 'Assists',
            'color': 'blue',
            'data': assist_data
        }
        points_series = {
            'name': 'Points',
            'color': 'purple',
            'data': point_data
        }
        stats_chart = {
            'chart': {'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Points Progression'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'series': [goals_series, assists_series, points_series]
        }
        return stats_chart
    def time_chart_gen(self, p):
        dataset = self.object_list.filter(player=p).order_by('game__date')
        dates = list()
        even_data = list()
        power_data = list()
        short_data = list()
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            even_data.append(entry.etoi)
            power_data.append(entry.pptoi)
            short_data.append(entry.shtoi)
        even_series = {
            'name': 'ETOI',
            'color': 'green',
            'data': even_data
        }
        power_series = {
            'name': 'PPTOI',
            'color': 'red',
            'data': power_data
        }
        short_series = {
            'name': 'SHTOI',
            'color': 'blue',
            'data': short_data
        }
        time_chart = {
            'chart': {'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Time on Ice'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'series': [even_series, power_series, short_series]
        }
        return time_chart
    def get(self, request, *args, **kwargs):
        first = self.object_list.order_by('player').first().player
        context = self.get_context_data(**kwargs)
        stats_chart = self.points_chart_gen(first)
        time_chart = self.time_chart_gen(first)
        context['stats_chart'] = json.dumps(stats_chart)
        context['time_chart'] = json.dumps(time_chart)
        context['current_skater'] = first.name
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            p = request.POST.get('playerId')
            stats_chart = self.points_chart_gen(p)
            time_chart = self.time_chart_gen(p)
            context = self.get_context_data(**kwargs)
            context['stats_chart'] = json.dumps(stats_chart)
            context['time_chart'] = json.dumps(time_chart)
            current = Player.objects.get(player_id=p)
            context['current_skater'] = current.name
            return render(request, self.template_name, context=context)
        except (Player.DoesNotExist, ValueError):
            first = self.object_list.order_by('player').first().player
            context = self.get_context_data(**kwargs)
            stats_chart = self.points_chart_gen(first)
            time_chart = self.time_chart_gen(first)
            context['stats_chart'] = json.dumps(stats_chart)
            context['time_chart'] = json.dumps(time_chart)
            context['current_skater'] = first.name
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