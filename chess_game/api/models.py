from django.db import models

class ChessGame(models.Model):
    board = models.CharField(default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", max_length=100)
    player_white = models.CharField(default="", max_length=50)  
    player_black = models.CharField(default="", max_length=50)
    player_white_time = models.IntegerField(default=0)
    player_black_time = models.IntegerField(default=0)
    initial_fen = models.CharField(max_length=255, default="startpos")
    moves = models.TextField(blank=True)  # Space-separated UCI moves eg. e2e4 e7e5 g1f3 b8c6 f1b5
    game_mode = models.CharField(default="", max_length=50)
    draw_offered_by = models.CharField(default="", max_length=5, null=True, blank=True)
    draw_accepted = models.BooleanField(default=False)
    resign = models.BooleanField(default=False)
    pgn = models.TextField(default="")
    game_over = models.BooleanField(default=False)
    game_over_reason = models.CharField(default="", max_length=50)
    result = models.CharField(default="", max_length=10,null=True, blank=True) #Game result 1-0 ,0-1 ,1/2-1/2
    
    def __str__(self):
        return f"Game {self.id}"
    
    
    
