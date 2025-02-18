from stockfish import Stockfish
import chess 


STOCKFISH_PATH = r"C:\app\stockfish\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(STOCKFISH_PATH)


def is_null_or_empty(value):
    return value is None or value == "" or (hasattr(value, '__len__') and len(value) == 0)

def make_engine_move( game, board) -> str:
        try:
            stockfish.set_fen_position(board.fen())
            engine_move = stockfish.get_best_move()
            if engine_move:
                game.board = board.fen()
                game.moves += f" {engine_move}"
                if chess.Move.from_uci(engine_move) not in board.legal_moves:
                    return ""
                board.push(chess.Move.from_uci(engine_move))
                game.board = board.fen()
            return engine_move
        except Exception:
            return False
        
def get_dic_value_by_key(dic, key):
    # Convert to a dictionary for quick access
    dictionary = dict(dic)

    # Access the key for 'Rapid'
    value = next(v for k, v in dictionary.items() if k == key)
    return value