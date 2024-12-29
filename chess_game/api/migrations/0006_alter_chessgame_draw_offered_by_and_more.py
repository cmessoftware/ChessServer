# Generated by Django 5.1.4 on 2024-12-29 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_chessgame_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chessgame',
            name='draw_offered_by',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='chessgame',
            name='game_over_reason',
            field=models.CharField(blank=True, choices=[('checkmate', 'Checkmate'), ('stalemate', 'Stalemate'), ('threefold_repetition', 'Threefold repetition'), ('insufficient_material', 'Insufficient material'), ('fifty_moves', 'Fifty moves'), ('time_control', 'Time control'), ('draw_offer', 'Draw offer'), ('resign', 'Resignation'), ('agreed_draw', 'Agreed draw')], max_length=50),
        ),
    ]
