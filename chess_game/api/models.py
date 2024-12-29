from django.db import models

class ChessGame(models.Model):
    GAME_MODE_CHOICES = [
        ('classic', 'Classic'),
        ('rapid', 'Rapid'),
        ('blitz', 'Blitz'),
        ('bullet', 'Bullet'),
    ]
    GAME_OVER_REASON_CHOICES = [
        ('checkmate', 'Checkmate'),
        ('stalemate', 'Stalemate'),
        ('threefold_repetition', 'Threefold repetition'),
        ('insufficient_material', 'Insufficient material'),
        ('fifty_moves', 'Fifty moves'),
        ('time_control', 'Time control'),
        ('resignation', 'Resignation'),
        ('draw_offer', 'Draw offer'),
        ('agreed_draw', 'Agreed draw'),
    ]
    
    board = models.CharField(default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", max_length=100, blank=False)
    event = models.CharField(default="Online game", max_length=50, blank=False)
    player_white = models.CharField(default="", max_length=50, blank=False)  
    player_black = models.CharField(default="", max_length=50, blank=False)
    player_white_time = models.IntegerField(default=0)
    player_black_time = models.IntegerField(default=0)
    initial_fen = models.CharField(max_length=255, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", blank=False)
    moves = models.TextField(default="", blank=True)  # Space-separated UCI moves eg. e2e4 e7e5 g1f3 b8c6 f1b5
    game_mode = models.CharField(
        max_length=50,
        choices=GAME_MODE_CHOICES,
        blank=False
    )
    initial_time = models.IntegerField(default=0)  # Initial time in seconds
    increment = models.IntegerField(default=0)  # Increment in seconds
    draw_offered_by = models.CharField(default="", max_length=5, null=True, blank=True)
    draw_accepted = models.BooleanField(default=False)
    resign = models.BooleanField(default=False)
    pgn = models.TextField(default="")
    game_over = models.BooleanField(default=False)
    game_over_reason = models.CharField(
        max_length=50,
        choices=GAME_OVER_REASON_CHOICES,
        blank=True   
    )
    result = models.CharField(default="*", max_length=10, blank=True) #Game result 1-0 ,0-1 ,1/2-1/2
    
    def __str__(self):
        return f"Game {self.id}"
    
    
    
