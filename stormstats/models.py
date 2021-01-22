from django.db import models

# Game model:
class Game(models.Model):
    game_id = models.PositiveIntegerField(primary_key=True)
    season = models.PositiveIntegerField()
    date = models.DateField()
    opponent = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    time = models.TimeField()

# Player model:
class Player(models.Model):
    player_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    jersey = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    height = models.CharField(max_length=5)
    weight = models.PositiveIntegerField()
    group = models.CharField(max_length=12)
    position = models.CharField(max_length=14)
    birthplace = models.CharField(max_length=50)
    birthdate = models.DateField()

# SkaterOverallStats model:
class SkaterOverallStats(models.Model):
    season = models.PositiveIntegerField()
    player = models.OneToOneField(Player, on_delete = models.CASCADE)
    games = models.PositiveIntegerField()
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    pim = models.CharField(max_length=6)
    plusmin = models.IntegerField()
    toipg = models.CharField(max_length=6)
    ppg = models.PositiveIntegerField()
    ppa = models.PositiveIntegerField()
    shg = models.PositiveIntegerField()
    sha = models.PositiveIntegerField()
    etoipg = models.CharField(max_length=6)
    shtoipg = models.CharField(max_length=6)
    pptoipg = models.CharField(max_length=6)
    shots = models.PositiveIntegerField()
    shotpct = models.DecimalField(max_digits=5, decimal_places=2)
    fopct = models.DecimalField(max_digits=5, decimal_places=2)
    blocks = models.PositiveIntegerField()
    hits = models.PositiveIntegerField()
    shifts = models.PositiveIntegerField()
    gwg = models.PositiveIntegerField()

    class Meta:
        unique_together = (("season","player"),)