from django.db import models

# Game model:
class Game(models.Model):
    game_id = models.PositiveIntegerField(primary_key=True)
    season = models.PositiveIntegerField()
    date = models.DateField()
    opponent = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    time = models.TimeField()
    result = models.CharField(max_length=12, null=True)
    played = models.BooleanField()

# Player model:
class Player(models.Model):
    player_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    jersey = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    height_str = models.CharField(max_length=5)
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    group = models.CharField(max_length=12)
    position = models.CharField(max_length=14)
    birthplace = models.CharField(max_length=50)
    bp_lat = models.DecimalField(max_digits=7, decimal_places=4)
    bp_long = models.DecimalField(max_digits=7, decimal_places=4)
    birthdate = models.DateField()

# SkaterOverallStats model:
class SkaterOverallStats(models.Model):
    season = models.PositiveIntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    games = models.PositiveIntegerField()
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    pim = models.PositiveIntegerField()
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
        constraints = [
            models.UniqueConstraint(fields= ['player','season'], name='unique_skater_season'),
        ]

# GoalieOverallStats model:
class GoalieOverallStats(models.Model):
    season = models.PositiveIntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    games = models.PositiveIntegerField()
    wins = models.PositiveIntegerField()
    losses = models.PositiveIntegerField()
    ties = models.PositiveIntegerField()
    started = models.PositiveIntegerField()
    saves = models.PositiveIntegerField()
    shotsa = models.PositiveIntegerField()
    goalsa = models.PositiveIntegerField()
    toipg = models.CharField(max_length=6)
    svpct = models.DecimalField(max_digits=5, decimal_places=2)
    gaa = models.DecimalField(max_digits=4, decimal_places=3)
    ot = models.PositiveIntegerField()
    shutouts = models.PositiveIntegerField()
    essaves = models.PositiveIntegerField()
    ppsaves = models.PositiveIntegerField()
    shsaves = models.PositiveIntegerField()
    esshots = models.PositiveIntegerField()
    ppshots = models.PositiveIntegerField()
    shshots = models.PositiveIntegerField()
    essvpct = models.DecimalField(max_digits=5, decimal_places=2)
    ppsvpct = models.DecimalField(max_digits=5, decimal_places=2)
    shsvpct = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['player','season'], name='unique_goalie_season'),
        ]

# SkaterGameStats model:
class SkaterGameStats(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    pim = models.PositiveIntegerField()
    plusmin = models.IntegerField()
    toi = models.CharField(max_length=6)
    ppg = models.PositiveIntegerField()
    ppa = models.PositiveIntegerField()
    shg = models.PositiveIntegerField()
    sha = models.PositiveIntegerField()
    etoi = models.CharField(max_length=6)
    shtoi = models.CharField(max_length=6)
    pptoi = models.CharField(max_length=6)
    shots = models.PositiveIntegerField()
    blocks = models.PositiveIntegerField()
    hits = models.PositiveIntegerField()
    fow = models.PositiveIntegerField()
    fot = models.PositiveIntegerField()
    ta = models.PositiveIntegerField()
    ga = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['player','game'], name='unique_skater_game'),
        ]

# GoalieGameStats model:
class GoalieGameStats(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    wl = models.CharField(max_length=2)
    goalsa = models.PositiveIntegerField()
    shotsa = models.PositiveIntegerField()
    saves = models.PositiveIntegerField()
    svpct = models.DecimalField(max_digits=5, decimal_places=2)
    toi = models.CharField(max_length=6)
    pim = models.PositiveIntegerField()
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    essaves = models.PositiveIntegerField()
    ppsaves = models.PositiveIntegerField()
    shsaves = models.PositiveIntegerField()
    esshots = models.PositiveIntegerField()
    ppshots = models.PositiveIntegerField()
    shshots = models.PositiveIntegerField()
    essvpct = models.DecimalField(max_digits=5, decimal_places=2)
    ppsvpct = models.DecimalField(max_digits=5, decimal_places=2)
    shsvpct = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['player','game'], name='unique_goalie_game'),
        ]