# Generated by Django 5.1.4 on 2025-01-10 23:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_remove_chessgame_draw_accepted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chessgame',
            name='game_over_type',
        ),
    ]
