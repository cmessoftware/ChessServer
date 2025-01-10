from rest_framework import serializers
from .models import ChessGame


class ChessGameSerializer(serializers.ModelSerializer):
    player_white = serializers.CharField(max_length=50, required=True, allow_blank=False)
    player_black = serializers.CharField(max_length=50, required=True, allow_blank=False)
    initial_time = serializers.IntegerField(required=True)
    increment = serializers.IntegerField(required=True)
    result = serializers.CharField(max_length=50, required=False, allow_blank=True)
    resign = serializers.CharField(max_length=50, required=False, allow_blank=True)
    game_over = serializers.BooleanField(default=False)
    game_over_reason = serializers.CharField(max_length=50, required=False, allow_blank=True)
    moves = serializers.CharField(max_length=500, required=False, allow_blank=True)
    game_mode = serializers.CharField(max_length=50, required=True, allow_blank=False)
    orientation = serializers.CharField(max_length=10, required=False, allow_blank=True)
    player_black = serializers.CharField(max_length=50, required=False, allow_blank=True)
    player_white = serializers.CharField(max_length=50, required=False, allow_blank=True)
    player_black_time = serializers.IntegerField(required=False)
    player_white_time = serializers.IntegerField(required=False)
    turn = serializers.CharField(max_length=10, required=False, allow_blank=True)
 
 
    class Meta:
        model = ChessGame
        fields = "__all__"
        
    # def validate_player_white(self, value):
    #     if not value.strip():
    #         raise serializers.ValidationError("Player White field cannot be empty.")
    #     return value