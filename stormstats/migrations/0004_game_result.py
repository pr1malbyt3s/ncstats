# Generated by Django 3.1.4 on 2021-03-02 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stormstats', '0003_auto_20210222_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='result',
            field=models.CharField(max_length=12, null=True),
        ),
    ]