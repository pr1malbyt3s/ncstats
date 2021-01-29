from django.views import generic
from .models import Player

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
        context['players'] = Player.objects.all()
        return context

'''
def player_list(request):
    players = Player.objects.all()
    return render(request, 'stormstats/index.html', {'players': players})
'''