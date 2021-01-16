from django.db import models

# Game model:
class Game(models.Model):
    game_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    opponent = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    time = models.TimeField()

# Player model:
class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    jersey = models.IntegerField()
    age = models.IntegerField()
    height = models.CharField(max_length=5)
    weight = models.IntegerField()
    group = models.CharField(max_length=12)
    position = models.CharField(max_length=14)
    birthplace = models.CharField(max_length=50)
    birthdate = models.DateField()