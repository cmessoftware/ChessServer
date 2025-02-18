# Generated by Django 5.1.4 on 2024-12-29 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chessgame',
            name='game_mode',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='game_over_reason',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='initial_fen',
            field=models.CharField(default='startpos', max_length=255),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='moves',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='player_black',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='player_black_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='player_white',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='chessgame',
            name='player_white_time',
            field=models.IntegerField(default=0),
        ),
    ]
