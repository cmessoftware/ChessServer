from django.shortcuts import render
from django.utils.timezone import now
from api.models import ChessGame

def chessboard_view(request):
    context = {
        'timestamp': now().timestamp()
    }
    return render(request, 'chessboard.html',context)
    
def get_game_feature(request , gameId):
    game = ChessGame.objects.get(id=gameId)
    game.game_over = True
    game.game_over_reason = 'checkmate'
    game.result = '1-0'
    game.moves = 'g2e4 e7e5 f2f3 d8h4#'
    game.current_turn = 'white'
    context = {
        'game': game,
        'timestamp': now().timestamp()
    }
    return render(request, 'chessboard.html',context)

