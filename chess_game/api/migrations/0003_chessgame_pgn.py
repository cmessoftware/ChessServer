# Generated by Django 5.1.4 on 2024-12-29 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_chessgame_game_mode_chessgame_game_over_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chessgame',
            name='pgn',
            field=models.TextField(default=''),
        ),
    ]