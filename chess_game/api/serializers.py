from rest_framework import serializers
from .models import ChessGame


class ChessGameSerializer(serializers.ModelSerializer):
    player_white = serializers.CharField(max_length=50, required=True, allow_blank=False)
    player_black = serializers.CharField(max_length=50, required=True, allow_blank=False)
    initial_time = serializers.IntegerField(required=True)
    increment = serializers.IntegerField(required=True)

    class Meta:
        model = ChessGame
        fields = [
            'id', 
            "moves",
            'player_white', 
            'player_black', 
            'game_mode',
            "game_over",
            "game_over_reason",
            "initial_time",
            "increment",
            "resign"
        ]
        
    def validate_player_white(self, value):
        if not value.strip():
            raise serializers.ValidationError("Player White field cannot be empty.")
        return value