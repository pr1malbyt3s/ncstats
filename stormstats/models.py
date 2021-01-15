from django.db import models

# Schedule model:
class Schedule(models.Model):
    game_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    opponent = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    time = models.TimeField()