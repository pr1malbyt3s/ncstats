# Generated by Django 3.1.4 on 2021-01-16 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stormstats', '0002_auto_20210116_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='age',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='player',
            name='jersey',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight',
            field=models.IntegerField(),
        ),
    ]