# Generated by Django 3.1.4 on 2021-01-23 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('season', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('opponent', models.CharField(max_length=30)),
                ('location', models.CharField(max_length=30)),
                ('time', models.TimeField()),
                ('played', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('player_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('jersey', models.PositiveIntegerField()),
                ('age', models.PositiveIntegerField()),
                ('height', models.CharField(max_length=5)),
                ('weight', models.PositiveIntegerField()),
                ('group', models.CharField(max_length=12)),
                ('position', models.CharField(max_length=14)),
                ('birthplace', models.CharField(max_length=50)),
                ('birthdate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SkaterOverallStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.PositiveIntegerField()),
                ('games', models.PositiveIntegerField()),
                ('goals', models.PositiveIntegerField()),
                ('assists', models.PositiveIntegerField()),
                ('points', models.PositiveIntegerField()),
                ('pim', models.CharField(max_length=6)),
                ('plusmin', models.IntegerField()),
                ('toipg', models.CharField(max_length=6)),
                ('ppg', models.PositiveIntegerField()),
                ('ppa', models.PositiveIntegerField()),
                ('shg', models.PositiveIntegerField()),
                ('sha', models.PositiveIntegerField()),
                ('etoipg', models.CharField(max_length=6)),
                ('shtoipg', models.CharField(max_length=6)),
                ('pptoipg', models.CharField(max_length=6)),
                ('shots', models.PositiveIntegerField()),
                ('shotpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fopct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('blocks', models.PositiveIntegerField()),
                ('hits', models.PositiveIntegerField()),
                ('shifts', models.PositiveIntegerField()),
                ('gwg', models.PositiveIntegerField()),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.player')),
            ],
            options={
                'unique_together': {('season', 'player')},
            },
        ),
        migrations.CreateModel(
            name='SkaterGameStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals', models.PositiveIntegerField()),
                ('assists', models.PositiveIntegerField()),
                ('points', models.PositiveIntegerField()),
                ('pim', models.CharField(max_length=6)),
                ('plusmin', models.IntegerField()),
                ('toi', models.CharField(max_length=6)),
                ('ppg', models.PositiveIntegerField()),
                ('ppa', models.PositiveIntegerField()),
                ('shg', models.PositiveIntegerField()),
                ('sha', models.PositiveIntegerField()),
                ('etoi', models.CharField(max_length=6)),
                ('shtoi', models.CharField(max_length=6)),
                ('pptoi', models.CharField(max_length=6)),
                ('shots', models.PositiveIntegerField()),
                ('blocks', models.PositiveIntegerField()),
                ('hits', models.PositiveIntegerField()),
                ('fow', models.PositiveIntegerField()),
                ('fot', models.PositiveIntegerField()),
                ('ta', models.PositiveIntegerField()),
                ('ga', models.PositiveIntegerField()),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.game')),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.player')),
            ],
            options={
                'unique_together': {('game', 'player')},
            },
        ),
        migrations.CreateModel(
            name='GoalieOverallStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.PositiveIntegerField()),
                ('games', models.PositiveIntegerField()),
                ('wins', models.PositiveIntegerField()),
                ('losses', models.PositiveIntegerField()),
                ('ties', models.PositiveIntegerField()),
                ('started', models.PositiveIntegerField()),
                ('saves', models.PositiveIntegerField()),
                ('shotsa', models.PositiveIntegerField()),
                ('goalsa', models.PositiveIntegerField()),
                ('toipg', models.CharField(max_length=6)),
                ('svpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('gaa', models.DecimalField(decimal_places=3, max_digits=4)),
                ('ot', models.PositiveIntegerField()),
                ('shutouts', models.PositiveIntegerField()),
                ('essaves', models.PositiveIntegerField()),
                ('ppsaves', models.PositiveIntegerField()),
                ('shsaves', models.PositiveIntegerField()),
                ('esshots', models.PositiveIntegerField()),
                ('ppshots', models.PositiveIntegerField()),
                ('shshots', models.PositiveIntegerField()),
                ('essvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('ppsvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('shsvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.player')),
            ],
            options={
                'unique_together': {('season', 'player')},
            },
        ),
        migrations.CreateModel(
            name='GoalieGameStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wl', models.CharField(max_length=2)),
                ('goalsa', models.PositiveIntegerField()),
                ('shotsa', models.PositiveIntegerField()),
                ('saves', models.PositiveIntegerField()),
                ('svpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('toi', models.CharField(max_length=6)),
                ('pim', models.CharField(max_length=6)),
                ('goals', models.PositiveIntegerField()),
                ('assists', models.PositiveIntegerField()),
                ('essaves', models.PositiveIntegerField()),
                ('ppsaves', models.PositiveIntegerField()),
                ('shsaves', models.PositiveIntegerField()),
                ('esshots', models.PositiveIntegerField()),
                ('ppshots', models.PositiveIntegerField()),
                ('shshots', models.PositiveIntegerField()),
                ('essvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('ppsvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('shsvpct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.game')),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stormstats.player')),
            ],
            options={
                'unique_together': {('game', 'player')},
            },
        ),
    ]
