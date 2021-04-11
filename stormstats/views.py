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
    model = Player
    template_name = 'stormstats/roster.html'
    context_object_name = 'players'
    def pos_chart_gen(self):
        dataset = self.model.objects.all()
        positions = list(dataset.order_by('position').values_list('position', flat=True).distinct())
        pos_data = list()
        for position in positions:
            count = 0
            for entry in dataset:
                if (entry.position == position):
                    count += 1
            pos_data.append(count)
        pos_series = {
            'name':'Position Count',
            'data':pos_data
        }
        pos_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Position Distribution'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Position'}, 'categories':positions},
            'yAxis': {'title': {'text':'Number of Players'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{point.y} Players'}}},
            'series' : [pos_series]
        }
        return pos_chart
    def age_chart_gen(self):
        dataset = self.model.objects.all().order_by('name')
        age_data = list()
        for entry in dataset:
            age_data.append({'name':entry.name, 'data':[[entry.jersey, entry.age]]})
        age_chart = {
            'chart': {'type':'scatter', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Age vs. Jersey'},
            'xAxis': {'title': {'text':'Jersey #'}},
            'yAxis': {'title': {'text':'Age'}},
            'tooltip': {'headerFormat':'', 'pointFormat':'<b>{series.name}</b><br>Age: {point.y}, Jersey: {point.x}'},
            'plotOptions' : {'series':{'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}'}}},
            'series': age_data
        }
        return age_chart
    def hw_chart_gen(self):
        dataset = self.model.objects.all().order_by('name')
        hw_data = list()
        for entry in dataset:
            hw_data.append({'name':entry.name, 'data':[[entry.weight, entry.height]]})
        hw_chart = {
            'chart': {'type':'scatter', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Roster Height vs. Weight'},
            'xAxis': {'title': {'text':'Weight (lbs)'}},
            'yAxis': {'title': {'text':'Height (in)'}},
            'tooltip': {'headerFormat':'', 'pointFormat':'<b>{series.name}</b><br>Height: {point.y}, Weight: {point.x}'},
            'plotOptions' : {'series':{'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}'}}},
            'series': hw_data
        }
        return hw_chart
    def map_chart_gen(self):
        dataset = self.model.objects.all().order_by('name')
        map_data = list()
        map_data.append({'name':'Birtplace Map', 'borderColor':'#A0A0A0', 'nullColor':'#ffffff', 'showInLegend':False})
        for entry in dataset:
            map_data.append({'type':'mappoint', 'name':entry.name, 'data':[{'name':entry.birthplace, 'lat':entry.bp_lat, 'lon':entry.bp_long}]})
        map_chart = {
            'chart': {'map':'custom/world', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Birthplaces'},
            'mapNavigation': {'enabled':True},
            'tooltip': {'headerFormat':'', 'pointFormat':'<b>{series.name}</b><br>Lat: {point.lat}, Lon: {point.lon}'},
            'series': map_data
        }
        return map_chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Roster"
        context['roster_activate'] = 'active'
        context['pos_chart'] = json.dumps(self.pos_chart_gen())
        context['age_chart'] = json.dumps(self.age_chart_gen())
        context['hw_chart'] = json.dumps(self.hw_chart_gen())
        context['map_chart'] = json.dumps(self.map_chart_gen())
        return context

class ScheduleView(generic.ListView):
    model = Game
    template_name = 'stormstats/schedule.html'
    context_object_name = 'games'
    played_games = model.objects.all().filter(played=True).order_by('date')
    remaining_games = model.objects.all().filter(played=False).order_by('date')
    def month_chart_gen(self):
        dataset = self.model.objects.all()
        months = list(dataset.dates('date', 'month'))
        opponents = list(dataset.order_by('opponent').values_list('opponent', flat=True).distinct())
        months_list = list()
        count_list =  list()
        for opponent in opponents:
            for month in months:
                x = dataset.filter(date__month=month.month, opponent=opponent).count()
                count_list.append([opponents.index(opponent), months.index(month), x])
        for month in months:
            months_list.append(month.strftime("%B"))
        max_count = max(item[2] for item in count_list)
        month_chart = {
            'chart': {'type':'heatmap', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Opponents Faced by Month'},
            'xAxis': {'categories':opponents},
            'colorAxis': {'min':0, 'max':max_count, 'minColor':'#ffffff', 'maxColor':'#ff0000'},
            'yAxis': {'categories':months_list, 'title':None, 'reversed':True},
            'tooltip': {'headerFormat':'', 'pointFormat':'{point.value} Games Played'},
            'series': [{'name':'Test', 'borderColor':'black', 'borderWidth':1, 'data':count_list, 'dataLabels': {'enabled':True}}]
        }
        return month_chart
    def results_chart_gen(self):
        dataset = self.model.objects.all()
        opponents = list(dataset.order_by('opponent').values_list('opponent', flat=True).distinct())
        results = ['W', 'L']
        count_list =  list()
        for opponent in opponents:
            for r in results:
                x = dataset.filter(played=True, result__startswith=r, opponent=opponent).count()
                count_list.append([opponents.index(opponent), results.index(r), x])
        max_count = max(item[2] for item in count_list)
        results_chart = {
            'chart': {'type':'heatmap', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Results by Opponent'},
            'xAxis': {'categories':opponents},
            'colorAxis': {'min':0, 'max':max_count, 'minColor':'#ffffff', 'maxColor':'#ff0000'},
            'yAxis': {'categories':results, 'title':None, 'reversed':True},
            'tooltip': {'headerFormat':'', 'pointFormat':'{point.value} Games'},
            'series': [{'name':'Test', 'borderColor':'black', 'borderWidth':1, 'data':count_list, 'dataLabels': {'enabled':True}}]
        }
        return results_chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Schedule"
        context['schedule_activate'] = 'active'
        context['played_games'] = self.played_games
        context['remaining_games'] = self.remaining_games
        context['month_chart'] = json.dumps(self.month_chart_gen())
        context['results_chart'] = json.dumps(self.results_chart_gen())
        return context

class SkaterStatsView(generic.ListView):
    model = SkaterOverallStats
    template_name = 'stormstats/skaterstats.html'
    context_object_name = 'skaterstats'
    def goals_chart_gen(self):
        dataset = self.model.objects.all().order_by('goals')
        goals_data = list()
        for entry in dataset:
            goals_data.append({'name':entry.player.name, 'data':[entry.goals]})
        goals_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Goals % Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Goals']},
            'yAxis': {'title': {'text':'Goals Percentage'}, 'stackLabels': {'enabled':True, 'format':'Total Goals: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y} ({point.percentage:.0f}%)'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'percent'}},
            'series' : goals_data
        }
        return goals_chart
    def assists_chart_gen(self):
        dataset = self.model.objects.all().order_by('assists')
        assists_data = list()
        for entry in dataset:
            assists_data.append({'name':entry.player.name, 'data':[entry.assists]})
        assists_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Assists % Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Assists']},
            'yAxis': {'title': {'text':'Assist Percentage'}, 'stackLabels': {'enabled':True, 'format':'Total Assists: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y} ({point.percentage:.0f}%)'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'percent'}},
            'series' : assists_data
        }
        return assists_chart
    def points_chart_gen(self):
        dataset = self.model.objects.all().order_by('points')
        points_data = list()
        for entry in dataset:
            points_data.append({'name':entry.player.name, 'data':[entry.points]})
        points_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Points % Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Points']},
            'yAxis': {'title': {'text':'Point Percentage'}, 'stackLabels': {'enabled':True, 'format':'Total Points: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y} ({point.percentage:.0f}%)'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'percent'}},
            'series' : points_data
        }
        return points_chart
    def pim_chart_gen(self):
        dataset = self.model.objects.all().order_by('pim')
        pim_data = list()
        for entry in dataset:
            pim_data.append({'name':entry.player.name, 'data':[entry.pim]})
        pim_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'PIM % Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Penalty Minutes']},
            'yAxis': {'title': {'text':'PIM Percentage'}, 'stackLabels': {'enabled':True, 'format':'Total Penalty Minutes: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y} ({point.percentage:.0f}%)'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'percent'}},
            'series' : pim_data
        }
        return pim_chart
    def plus_chart_gen(self):
        dataset = self.model.objects.all().order_by('plusmin')
        plus_data = list()
        for entry in dataset:
            plus_data.append({'name':entry.player.name, 'data':[entry.plusmin]})
        plus_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': '+/- Distribution'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Plus Minus']},
            'yAxis': {'title': {'text':'Rating'}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}},
            'series' : plus_data
        }
        return plus_chart
    def shot_chart_gen(self):
        dataset = self.model.objects.all()
        shot_data = list()
        for entry in dataset:
            shot_data.append({'name':entry.player.name, 'data':[[entry.shotpct, entry.shots]]})
        shot_chart = {
            'chart': {'type':'scatter', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Shots vs. Shot%'},
            'xAxis': {'title': {'text':'Shot Percentage'}},
            'yAxis': {'title': {'text':'Shots'}},
            'tooltip' : {'pointFormat':'Shots Taken: {point.y}</br>Shot%: {point.x}'},
            'plotOptions' : {'series':{'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.x}%'}}},
            'series': shot_data
        }
        return shot_chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals_chart = self.goals_chart_gen()
        context['goals_chart'] = json.dumps(goals_chart)
        assists_chart = self.assists_chart_gen()
        context['assists_chart'] = json.dumps(assists_chart)
        points_chart = self.points_chart_gen()
        context['points_chart'] = json.dumps(points_chart)
        pim_chart = self.pim_chart_gen()
        context['pim_chart'] = json.dumps(pim_chart)
        plus_chart = self.plus_chart_gen()
        context['plus_chart'] = json.dumps(plus_chart)
        shot_chart = self.shot_chart_gen()
        context['shot_chart'] = json.dumps(shot_chart)
        context['title'] = "StormStats - Skater Stats"
        context['skaterstats_activate'] = 'active'
        return context

class GoalieStatsView(generic.ListView):
    model = GoalieOverallStats
    template_name = 'stormstats/goaliestats.html'
    context_object_name = 'goaliestats'
    def wlt_chart_gen(self):
        dataset = self.model.objects.all().order_by('player__name')
        wlt_data = list()
        for entry in dataset:
            wlt_data.append([entry.player.name + ' Wins', entry.wins])
            wlt_data.append([entry.player.name + ' Losses', entry.losses])
        wlt_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Goalie Results Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'plotOptions': {'pie': {'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'distance':-30}, 'startAngle':-90, 'endAngle':90, 'center':['50%', '75%'], 'size':'150%'}},
            'tooltip' : {'headerFormat':'{point.key}: ', 'pointFormat':'{point.y}'},
            'series': [{'type':'pie', 'data':wlt_data}]
        }
        return wlt_chart
    def gaa_chart_gen(self):
        dataset = self.model.objects.all().order_by('player__name')
        gaa_data = list()
        for entry in dataset:
            gaa_data.append({'name':entry.player.name, 'data':[[entry.svpct, entry.gaa]]})
        gaa_chart = {
            'chart': {'type':'scatter', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'GAA vs. Save Percentage'},
            'xAxis': {'title': {'text':'Save Percentage'}},
            'yAxis': {'title': {'text':'Goals Against Average'}},
            'tooltip' : {'pointFormat':'GAA: {point.y}</br>Save%: {point.x}'},
            'plotOptions' : {'series':{'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.x}%'}}},
            'series': gaa_data
        }
        return gaa_chart
    def save_chart_gen(self):
        dataset = self.model.objects.all().order_by('player__name')
        name_data = list()
        essave_data = list()
        ppsave_data = list()
        shsave_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            essave_data.append(entry.essaves)
            ppsave_data.append(entry.ppsaves)
            shsave_data.append(entry.shsaves)
        save_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Save Type Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Save Count'}, 'stackLabels': {'enabled':True, 'format':'Total Saves: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'normal'}},
            'series' : [{'name':'Shorthanded Saves', 'data':shsave_data}, {'name':'Power Play Saves', 'data': ppsave_data}, {'name':'Even Saves', 'data':essave_data}]
        }
        return save_chart
    def shot_chart_gen(self):
        dataset = self.model.objects.all().order_by('player__name')
        name_data = list()
        esshot_data = list()
        ppshot_data = list()
        shshot_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            esshot_data.append(entry.esshots)
            ppshot_data.append(entry.ppshots)
            shshot_data.append(entry.shshots)
        shot_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Shots Faced Type Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Shot Count'}, 'stackLabels': {'enabled':True, 'format':'Total Shots Faced: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'normal'}},
            'series' : [{'name':'Shorthanded Shots', 'data':shshot_data}, {'name':'Power Play Shots', 'data': ppshot_data}, {'name':'Even Shots', 'data':esshot_data}]
        }
        return shot_chart
    def svpct_chart_gen(self):
        dataset = self.model.objects.all().order_by('player__name')
        name_data = list()
        svpct_data = list()
        essvpct_data = list()
        ppsvpct_data = list()
        shsvpct_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            svpct_data.append(entry.svpct*100)
            essvpct_data.append(entry.essvpct)
            ppsvpct_data.append(entry.ppsvpct)
            shsvpct_data.append(entry.shsvpct)
        svpct_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Save Percentage Distribution'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Save Percentage'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}},
            'series' : [{'name':'Overall Save Percentage', 'data':svpct_data}, {'name':'Even Save Percentage', 'data':essvpct_data}, {'name':'Power Play Save Percentage', 'data': ppsvpct_data}, {'name':'Shorthanded Save Percentage', 'data':shsvpct_data}]
        }
        return svpct_chart    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Stats"
        context['goaliestats_activate'] = 'active'
        context['wlt_chart'] = json.dumps(self.wlt_chart_gen())
        context['gaa_chart'] = json.dumps(self.gaa_chart_gen())
        context['save_chart'] = json.dumps(self.save_chart_gen())
        context['shot_chart'] = json.dumps(self.shot_chart_gen())
        context['svpct_chart'] = json.dumps(self.svpct_chart_gen())
        return context

class SkaterGameStatsByGameView(generic.ListView):
    model = SkaterGameStats
    template_name = 'stormstats/skatergamestats/skaterbygame.html'
    context_object_name = 'skatergamestats'
    games = Game.objects.all().filter(played=True).order_by('-date')
    def zero_check(self, v:int)->int:
            if v > 0:
                return v
            return None
    def stack_chart_gen(self, g):
        dataset = self.model.objects.all().filter(game=g).order_by('goals')
        goals_data = list()
        for entry in dataset:
            goals_data.append({'name':entry.player.name, 'data':[self.zero_check(entry.goals), self.zero_check(entry.assists), self.zero_check(entry.points)]})
        goals_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Game Points Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Goals', 'Assists', 'Points']},
            'yAxis': {'title': {'text':'Value Count'}, 'stackLabels': {'enabled':True, 'format':'Total {series.name}: {total}', 'overflow':'allow', 'crop':False}},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'normal'}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'series' : goals_data
        }
        return goals_chart
    def toi_chart_gen(self, g):
        dataset = self.model.objects.all().filter(game=g).order_by('toi')
        def time_to_seconds(time_string:str)-> int:
            x = time_string.split(':')
            minutes = int(x[0])
            seconds = int(x[1])
            return (60*minutes) + seconds
        name_data = list()
        etoi_data = list()
        pptoi_data = list()
        shtoi_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            etoi_data.append(time_to_seconds(entry.etoi))
            pptoi_data.append(time_to_seconds(entry.pptoi))
            shtoi_data.append(time_to_seconds(entry.shtoi))
        toi_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Time on Ice Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Time on Ice(s)'}, 'stackLabels': {'enabled':True, 'format':'Total TOI(s): {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'normal'}},
            'series' : [{'name':'SHTOI', 'data':shtoi_data}, {'name':'PPTOI', 'data': pptoi_data}, {'name':'ETOI', 'data':etoi_data}]
        }
        return toi_chart
    def plus_chart_gen(self, g):
        dataset = self.model.objects.all().filter(game=g).order_by('plusmin')
        plus_data = list()
        for entry in dataset:
            plus_data.append({'name':entry.player.name, 'data':[entry.plusmin]})
        plus_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': '+/- Distribution'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':['Plus Minus']},
            'yAxis': {'title': {'text':'Rating'}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}},
            'series' : plus_data
        }
        return plus_chart
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats - By Game"
        context['skatergamestats_activate'] = 'active'
        context['games'] = self.games
        return context
    def get(self, request, *args, **kwargs):
        recent = self.games.latest('date')
        self.object_list = self.model.objects.filter(game=recent.game_id)
        context = self.get_context_data(**kwargs)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        context['stack_chart'] = json.dumps(self.stack_chart_gen(recent.game_id))
        context['toi_chart'] = json.dumps(self.toi_chart_gen(recent.game_id))
        context['plus_chart'] = json.dumps(self.plus_chart_gen(recent.game_id))
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            g = request.POST.get('gameId')
            self.object_list = self.model.objects.filter(game=g)
            recent = self.games.get(game_id=g)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['stack_chart'] = json.dumps(self.stack_chart_gen(g))
            context['toi_chart'] = json.dumps(self.toi_chart_gen(g))
            context['plus_chart'] = json.dumps(self.plus_chart_gen(g))
            return render(request, self.template_name, context=context)
        except (Game.DoesNotExist, ValueError):
            recent = self.games.latest('date')
            self.object_list = self.model.objects.filter(game=recent.game_id)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['stack_chart'] = json.dumps(self.stack_chart_gen(recent.game_id))
            context['toi_chart'] = json.dumps(self.toi_chart_gen(recent.game_id))
            context['plus_chart'] = json.dumps(self.plus_chart_gen(recent.game_id))
            context['error_message'] = "Please select a valid game."
            return render(request, self.template_name, context=context)
        
class SkaterGameStatsByPlayerView(generic.ListView):
    model = SkaterGameStats
    template_name = 'stormstats/skatergamestats/skaterbyplayer.html'
    context_object_name = 'skatergamestats'
    players = Player.objects.all().filter(group__in=['Forward', 'Defenseman']).order_by('name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Skater Game Stats - By Player"
        context['skatergamestats_activate'] = 'active'
        context['players'] = self.players
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
            'color': 'black',
            'dashStyle': 'longdash',
            'data': goal_data,
            'marker': {
                'fillColor':'red'
            }
        }
        assists_series = {
            'name': 'Assists',
            'color': 'black',
            'dashStyle': 'dot',
            'data': assist_data,
            'marker': {
                'fillColor':'gold'
            }
        }
        points_series = {
            'name': 'Points',
            'color': 'black',
            'data': point_data,
            'marker': {
                'fillColor':'orange'
            }
        }
        stats_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Points Progression'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text': 'Point Count'}},
            'series': [goals_series, assists_series, points_series]
        }
        return stats_chart
    def time_chart_gen(self, p):
        dataset = self.object_list.filter(player=p).order_by('game__date')
        def time_to_seconds(time_string:str)-> int:
            x = time_string.split(':')
            minutes = int(x[0])
            seconds = int(x[1])
            return (60*minutes) + seconds
        dates = list()
        even_data = list()
        power_data = list()
        short_data = list()
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            even_data.append(time_to_seconds(entry.etoi))
            power_data.append(time_to_seconds(entry.pptoi))
            short_data.append(time_to_seconds(entry.shtoi))
        even_series = {
            'name': 'ETOI',
            'color': 'black',
            'data': even_data,
            'marker': {
                'fillColor':'orange'
            }
        }
        power_series = {
            'name': 'PPTOI',
            'color': 'black',
            'data': power_data,
            'dashStyle': 'longdash',
            'marker': {
                'fillColor':'red'
            }
        }
        short_series = {
            'name': 'SHTOI',
            'color': 'black',
            'data': short_data,
            'dashStyle': 'dot',
            'marker': {
                'fillColor':'orange'
            }
        }
        time_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Time on Ice'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Time on Ice(s)'}},
            'series': [even_series, power_series, short_series]
        }
        return time_chart
    def plus_chart_gen(self, p):
        dataset = self.object_list.filter(player=p).order_by('game__date')
        dates = list()
        plus_data = list()
        pm = 0
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            pm += int(entry.plusmin)
            plus_data.append(pm)
        pm_series = {
            'name': '+/-',
            'color': 'black',
            'data': plus_data
        }
        plus_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Player Plus/Minus Progression'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Rating'}},
            'series': [pm_series]
        }
        return plus_chart
    def pointsopp_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        opponents = list(dataset.order_by('game__opponent').values_list('game__opponent', flat=True).distinct())
        points_data = list()
        for opponent in opponents:
            points = 0
            for entry in dataset:
                if (entry.game.opponent == opponent):
                    points += entry.points
            points_data.append(points)
        points_series = {
            'name':'Player Points',
            'data':points_data
        }
        pointsopp_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Points Per Opponent'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Opponent'}, 'categories':opponents},
            'yAxis': {'title': {'text':'Points Per Opponent'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor': 'black', 'color':'white'}}},
            'series' : [points_series]
        }
        return pointsopp_chart
    def plusopp_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        opponents = list(dataset.order_by('game__opponent').values_list('game__opponent', flat=True).distinct())
        plus_data = list()
        for opponent in opponents:
            rating = 0
            for entry in dataset:
                if (entry.game.opponent == opponent):
                    rating += int(entry.plusmin)
            plus_data.append(rating)
        plus_series = {
            'name':'Player Rating',
            'data':plus_data
        }
        plusopp_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Rating Per Opponent'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Opponent'}, 'categories':opponents},
            'yAxis': {'title': {'text':'Rating'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor': 'black', 'color':'white'}}},
            'series' : [plus_series]
        }
        return plusopp_chart
    def get(self, request, *args, **kwargs):
        first = self.players.first()
        self.object_list = self.model.objects.filter(player=first.player_id)
        context = self.get_context_data(**kwargs)
        context['stats_chart'] = json.dumps(self.points_chart_gen(first))
        context['time_chart'] = json.dumps(self.time_chart_gen(first))
        context['plus_chart'] = json.dumps(self.plus_chart_gen(first))
        context['pointsopp_chart'] = json.dumps(self.pointsopp_chart_gen(first))
        context['plusopp_chart'] = json.dumps(self.plusopp_chart_gen(first))
        context['current_skater'] = first.name
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            p = request.POST.get('playerId')
            current = self.players.get(player_id=p)
            self.object_list = self.model.objects.filter(player=p)
            context = self.get_context_data(**kwargs)
            context['stats_chart'] = json.dumps(self.points_chart_gen(p))
            context['time_chart'] = json.dumps(self.time_chart_gen(p))
            context['plus_chart'] = json.dumps(self.plus_chart_gen(p))
            context['pointsopp_chart'] = json.dumps(self.pointsopp_chart_gen(p))
            context['plusopp_chart'] = json.dumps(self.plusopp_chart_gen(p))
            context['current_skater'] = current.name
            return render(request, self.template_name, context=context)
        except (Player.DoesNotExist, ValueError):
            first = self.players.first()
            self.object_list = self.model.objects.filter(player=first.player_id)
            context = self.get_context_data(**kwargs)
            context['stats_chart'] = json.dumps(self.points_chart_gen(first))
            context['time_chart'] = json.dumps(self.time_chart_gen(first))
            context['plus_chart'] = json.dumps(self.plus_chart_gen(first))
            context['pointsopp_chart'] = json.dumps(self.pointsopp_chart_gen(first))
            context['plusopp_chart'] = json.dumps(self.plusopp_chart_gen(first))
            context['current_skater'] = first.name
            context['error_message'] = "Please select a valid player."
            return render(request, self.template_name, context=context)

class GoalieGameStatsByGameView(generic.ListView):
    model = GoalieGameStats
    template_name = 'stormstats/goaliegamestats/goaliebygame.html'
    context_object_name = 'goaliegamestats'
    games = Game.objects.all().filter(played=True).order_by('-date')
    def save_chart_gen(self, g):
        dataset = self.model.objects.all().filter(game=g)
        name_data = list()
        essave_data = list()
        ppsave_data = list()
        shsave_data = list()
        esshot_data = list()
        ppshot_data = list()
        shshot_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            essave_data.append(entry.essaves)
            ppsave_data.append(entry.ppsaves)
            shsave_data.append(entry.shsaves)
            esshot_data.append(entry.esshots)
            ppshot_data.append(entry.ppshots)
            shshot_data.append(entry.shshots)
        save_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Save/Shot Type Breakdown'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Save/Shot Count'}, 'stackLabels': {'enabled':True, 'color':'black', 'format':'Total {stack}: {total}', 'overflow':'allow', 'crop':False}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}, 'column': {'stacking':'normal'}},
            'series' : [{
                'name':'Shorthanded Saves', 'data':shsave_data, 'stack':'Saves'
            }, {
                'name':'Power Play Saves', 'data': ppsave_data, 'stack':'Saves'
            }, {
                'name':'Even Saves', 'data':essave_data, 'stack':'Saves'
            }, {
                'name':'Shorthanded Shots', 'data':shshot_data, 'stack':'Shots'
            }, {
                'name':'Power Play Shots', 'data': ppshot_data, 'stack':'Shots'
            }, {
                'name':'Even Shots', 'data':esshot_data, 'stack':'Shots'
            }]
        }
        return save_chart
    def svpct_chart_gen(self, g):
        dataset = self.model.objects.all().filter(game=g)
        name_data = list()
        svpct_data = list()
        essvpct_data = list()
        ppsvpct_data = list()
        shsvpct_data = list()
        for entry in dataset:
            name_data.append(entry.player.name)
            svpct_data.append(entry.svpct)
            essvpct_data.append(entry.essvpct)
            ppsvpct_data.append(entry.ppsvpct)
            shsvpct_data.append(entry.shsvpct)
        svpct_chart = {
            'chart': {'type':'column', 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Save Percentage Distribution'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'categories':name_data},
            'yAxis': {'title': {'text':'Save Percentage'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'<b>{point.x}</b><br/>', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'allowOverlap':True, 'backgroundColor':'black', 'color':'white', 'format':'{series.name}: {point.y}'}}},
            'series' : [{'name':'Overall Save Percentage', 'data':svpct_data}, {'name':'Even Save Percentage', 'data':essvpct_data}, {'name':'Power Play Save Percentage', 'data': ppsvpct_data}, {'name':'Shorthanded Save Percentage', 'data':shsvpct_data}]
        }
        return svpct_chart  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Game Stats - By Game"
        context['goaliegamestats_activate'] = 'active'
        context['games'] = self.games
        return context
    def get(self, request, *args, **kwargs):
        recent = self.games.latest('date')
        self.object_list = self.model.objects.filter(game=recent.game_id)
        context = self.get_context_data(**kwargs)
        context['current_game'] = str(recent.date) + " - " + recent.opponent
        context['save_chart'] = json.dumps(self.save_chart_gen(recent.game_id))
        context['svpct_chart'] = json.dumps(self.svpct_chart_gen(recent.game_id))
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        try:
            g = request.POST.get('gameId')
            self.object_list = self.model.objects.filter(game=g)
            recent = self.games.get(game_id=g)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['save_chart'] = json.dumps(self.save_chart_gen(g))
            context['svpct_chart'] = json.dumps(self.svpct_chart_gen(recent.game_id))
            return render(request, self.template_name, context=context)
        except (Game.DoesNotExist, ValueError):
            recent = self.games.latest('date')
            self.object_list = self.model.objects.filter(game=recent.game_id)
            context = self.get_context_data(**kwargs)
            context['current_game'] = str(recent.date) + " - " + recent.opponent
            context['save_chart'] = json.dumps(self.save_chart_gen(recent.game_id))
            context['svpct_chart'] = json.dumps(self.svpct_chart_gen(recent.game_id))
            context['error_message'] = "Please select a valid game."
            return render(request, self.template_name, context=context)

class GoalieGameStatsByPlayerView(generic.ListView):
    model = GoalieGameStats
    template_name = 'stormstats/goaliegamestats/goaliebyplayer.html'
    context_object_name = 'goaliegamestats'
    players = Player.objects.all().filter(group='Goalie').order_by('name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "StormStats - Goalie Game Stats - By Player"
        context['goaliegamestats_activate'] = 'active'
        context['players'] = self.players
        return context
    def save_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        dates = list()
        save_data = list()
        essave_data = list()
        ppsave_data = list()
        shsave_data = list()
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            save_data.append(entry.saves)
            essave_data.append(entry.essaves)
            ppsave_data.append(entry.ppsaves)
            shsave_data.append(entry.shsaves)
        save_series = {
            'name': 'Total Saves',
            'color': 'black',
            'data': save_data
        }
        essave_series = {
            'name': 'Even Saves',
            'color': 'black',
            'dashStyle': 'longdash',
            'data': essave_data
        }
        ppsave_series = {
            'name': 'PP Saves',
            'color': 'black',
            'dashStyle': 'shortdot',
            'data': ppsave_data
        }
        shsave_series = {
            'name': 'SH Saves',
            'color': 'black',
            'dashStyle': 'dashdot',
            'data': shsave_data
        }
        save_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Saves Per Game'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Save Count'}},
            'series': [save_series, essave_series, ppsave_series, shsave_series]
        }
        return save_chart
    def shot_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        dates = list()
        shot_data = list()
        esshot_data = list()
        ppshot_data = list()
        shshot_data = list()
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            shot_data.append(entry.shotsa)
            esshot_data.append(entry.esshots)
            ppshot_data.append(entry.ppshots)
            shshot_data.append(entry.shshots)
        shot_series = {
            'name': 'Total Shots Against',
            'color': 'black',
            'data': shot_data
        }
        esshot_series = {
            'name': 'Even Shots Against',
            'color': 'black',
            'dashStyle': 'longdash',
            'data': esshot_data
        }
        ppshot_series = {
            'name': 'PP Shots Against',
            'color': 'black',
            'dashStyle': 'shortdot',
            'data': ppshot_data
        }
        shshot_series = {
            'name': 'SH Shots Against',
            'color': 'black',
            'dashStyle': 'dashdot',
            'data': shshot_data
        }
        shot_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Shots Against Per Game'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Shot Count'}},
            'series': [shot_series, esshot_series, ppshot_series, shshot_series]
        }
        return shot_chart
    def svpct_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        dates = list()
        svpct_data = list()
        essvpct_data = list()
        ppsvpct_data = list()
        shsvpct_data = list()
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            svpct_data.append(entry.svpct)
            essvpct_data.append(entry.essvpct)
            ppsvpct_data.append(entry.ppsvpct)
            shsvpct_data.append(entry.shsvpct)
        svpct_series = {
            'name': 'Total Save %',
            'color': 'black',
            'data': svpct_data
        }
        essvpct_series = {
            'name': 'Even Save %',
            'color': 'black',
            'dashStyle': 'longdash',
            'data': essvpct_data
        }
        ppsvpct_series = {
            'name': 'PP Save %',
            'color': 'black',
            'dashStyle': 'shortdot',
            'data': ppsvpct_data
        }
        shsvpct_series = {
            'name': 'SH Save %',
            'color': 'black',
            'dashStyle': 'dashdot',
            'data': shsvpct_data
        }
        svpct_chart = {
            'chart': {'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Save Percentage Per Game'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Save Percentage'}},
            'series': [svpct_series, essvpct_series, ppsvpct_series, shsvpct_series]
        }
        return svpct_chart
    def goal_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        dates = list()
        goal_data = list()
        shot_data = list()
        goalsA = 0
        shotsA = 0
        for entry in dataset:
            dates.append((Game.objects.values_list('date', flat=True).get(game_id=entry.game_id)).strftime("%m-%d-%Y"))
            goalsA += entry.goalsa
            shotsA += entry.shotsa
            goal_data.append(goalsA)
            shot_data.append(shotsA)
        goal_series = {
            'name': 'Goals Against',
            'color': '#ff0000',
            'fillOpacity': 0.95,
            'data': goal_data
        }
        shot_series = {
            'name': 'Shots Against',
            'color': '#ffff00',
            'fillOpacity': 0.75,
            'data': shot_data
        }
        goal_chart = {
            'chart': {'type':'area', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Shots vs. Goals Progression'},
            'xAxis': {'title': {'text':'Game Date'}, 'categories':dates},
            'yAxis': {'title': {'text':'Shot/Goal Count'}},
            'plotOptions': {'area': {'marker': {'enabled':False, 'symbol':'circle', 'radius':2, 'states': {'hover': {'enabled':True}}}}},
            'series': [goal_series, shot_series]
        }
        return goal_chart
    def results_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        opponents = list(dataset.order_by('game__opponent').values_list('game__opponent', flat=True).distinct())
        results = ['W', 'L']
        count_list =  list()
        for opponent in opponents:
            for r in results:
                x = dataset.filter(wl=r, game__opponent=opponent).count()
                count_list.append([opponents.index(opponent), results.index(r), x])
        max_count = max(item[2] for item in count_list)
        results_chart = {
            'chart': {'type':'heatmap', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text':'Goalie Decision by Opponent'},
            'xAxis': {'categories':opponents},
            'colorAxis': {'min':0, 'max':max_count, 'minColor':'#ffffff', 'maxColor':'#ff0000'},
            'yAxis': {'categories':results, 'title':None, 'reversed':True},
            'tooltip': {'headerFormat':'', 'pointFormat':'{point.value} Games'},
            'series': [{'name':'Test', 'borderColor':'black', 'borderWidth':1, 'data':count_list, 'dataLabels': {'enabled':True}}]
        }
        return results_chart
    def svpctopp_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        opponents = list(dataset.order_by('game__opponent').values_list('game__opponent', flat=True).distinct())
        svpct_data = list()
        for opponent in opponents:
            shotsA = 0
            saves = 0
            for entry in dataset:
                if (entry.game.opponent == opponent):
                    shotsA += entry.shotsa
                    saves += entry.saves
            try:
                svpct = (saves/shotsA)
            except ZeroDivisionError:
                svpct = 0
            svpct_data.append(float('{0:.3}'.format(float(svpct))))
        svpctopp_series = {
            'name':'Goalie Save%',
            'data':svpct_data
        }
        svpctopp_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'Save Percentage Per Opponent'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis' : {'title': {'text':'Opponent'}, 'categories':opponents},
            'yAxis': {'title': {'text':'GAA'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white'}}},
            'series' : [svpctopp_series]
        }
        return svpctopp_chart
    def gaaopp_chart_gen(self, p):
        dataset = self.model.objects.all().filter(player=p).order_by('game__date')
        opponents = list(dataset.order_by('game__opponent').values_list('game__opponent', flat=True).distinct())
        gaa_data = list()
        for opponent in opponents:
            games = 0
            goalsA = 0
            for entry in dataset:
                if (entry.game.opponent == opponent):
                    goalsA += entry.goalsa
                    games += 1
            gaa = (goalsA/games)
            gaa_data.append(float('{0:.3}'.format(float(gaa))))
        gaaopp_series = {
            'name':'Goalie GAA',
            'data':gaa_data
        }
        gaaopp_chart = {
            'chart': {'type':'column', 'height':600, 'borderColor':'black', 'borderWidth':2},
            'credits': {'enabled':False},
            'title': {'text': 'GAA Per Opponent'},
            'colorAxis': {'minColor':'#ffff00', 'maxColor':'#ff0000'},
            'xAxis' : {'title': {'text':'Opponent'}, 'categories':opponents},
            'yAxis': {'title': {'text':'GAA'}, 'stackLabels': {'enabled':True}},
            'tooltip': {'headerFormat':'', 'pointFormat':'{series.name}: {point.y}'},
            'plotOptions' : {'series':{'borderColor':'black', 'dataLabels':{'enabled':True, 'backgroundColor':'black', 'color':'white'}}},
            'series' : [gaaopp_series]
        }
        return gaaopp_chart 
    def get(self, request, *args, **kwargs):
        first = self.players.first()
        self.object_list = self.model.objects.filter(player=first.player_id)
        context = self.get_context_data(**kwargs)
        context['current_goalie'] = first.name
        context['save_chart'] = json.dumps(self.save_chart_gen(first))
        context['shot_chart'] = json.dumps(self.shot_chart_gen(first))
        context['svpct_chart'] = json.dumps(self.svpct_chart_gen(first))
        context['goal_chart'] = json.dumps(self.goal_chart_gen(first))
        context['results_chart'] = json.dumps(self.results_chart_gen(first))
        context['svpctopp_chart'] = json.dumps(self.svpctopp_chart_gen(first))
        context['gaaopp_chart'] = json.dumps(self.gaaopp_chart_gen(first))
        return render(request, self.template_name, context=context)
    def post(self, request, *args, **kwargs):
        p = request.POST.get('playerId')
        try:
            p = request.POST.get('playerId')
            current = self.players.get(player_id=p)
            self.object_list = self.model.objects.filter(player=p)
            context = self.get_context_data(**kwargs)
            context['current_goalie'] = current.name
            context['save_chart'] = json.dumps(self.save_chart_gen(p))
            context['shot_chart'] = json.dumps(self.shot_chart_gen(p))
            context['svpct_chart'] = json.dumps(self.svpct_chart_gen(p))
            context['goal_chart'] = json.dumps(self.goal_chart_gen(p))
            context['results_chart'] = json.dumps(self.results_chart_gen(p))
            context['svpctopp_chart'] = json.dumps(self.svpctopp_chart_gen(p))
            context['gaaopp_chart'] = json.dumps(self.gaaopp_chart_gen(p))
            return render(request, self.template_name, context=context)
        except (Player.DoesNotExist, ValueError):
            first = self.players.first()
            self.object_list = self.model.objects.filter(player=first.player_id)
            context = self.get_context_data(**kwargs)
            context['current_goalie'] = first.name
            context['save_chart'] = json.dumps(self.save_chart_gen(first))
            context['shot_chart'] = json.dumps(self.shot_chart_gen(first))
            context['svpct_chart'] = json.dumps(self.svpct_chart_gen(first))
            context['goal_chart'] = json.dumps(self.goal_chart_gen(first))
            context['results_chart'] = json.dumps(self.results_chart_gen(first))
            context['svpctopp_chart'] = json.dumps(self.svpctopp_chart_gen(first))
            context['gaaopp_chart'] = json.dumps(self.gaaopp_chart_gen(first))
            context['error_message'] = "Please select a valid player."
            return render(request, self.template_name, context=context)