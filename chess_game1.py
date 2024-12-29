import chess
import chess.pgn
from stockfish import Stockfish
import threading



RESULT_PREFIX = "Result: "

class ChessGame1:
    
    game_state = {
        "draw_offered_by": None, #white or black
        "draw_accepted": False,
        "dismissed:": False,   
    }
    
    def __init__(self):
        self.lock = threading.Lock()
        self.board = chess.Board()
        engine_path = ".\\stockfish-windows-x86-64-avx2"
        self.stockfish = Stockfish(engine_path)
        self.set_depth(10)

    def get_board(self):
        return self.board

    def get_stockfish(self):
        return self.stockfish

    def get_legal_moves(self):
        return self.board.legal_moves

    def get_fen(self):
        return self.board.fen()

    def get_pgn(self):
        game = chess.pgn.Game.from_board(self.board)
        node = game
        for move in self.board.move_stack:
            node = node.add_variation(move)
        return str(game)
    
    def offer_draw(self, game_state, player):  
        if game_state["draw_offered_by"] is None:
            game_state["draw_offered_by"] = player
            print(f"{player} has offered a draw.")
        else:
            print(f"{game_state['draw_offered_by']} has already offered a draw.")
    
    def accept_draw(self, game_state, board):
        if game_state["draw_offered_by"] is not None:
            print("Draw accepted.")
            game_state["draw_accepted"] = True
            self.board.result = "1/2-1/2"
            return True
        else:
            print("No draw offered to accept.")
            return False
    
    def reject_draw(self, game_state):
        if game_state["draw_offered_by"] is not None:
            print(f"{game_state['draw_offered_by']}'s draw offer has been rejected.")
            game_state["draw_offered_by"] = None
            return True
        else:
            print("No draw offered to reject.")
    
    def resign_game(self, game_state):
        game_state["dismissed"] = True
        print("Game dismissed.")
     
    def make_move(self, move):
        try:
            
            #Parse and validate chess move
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                self.board.set_fen(self.board.fen())
                return True
            else:
                return False
            
        except  ValueError:
            return False

    def is_checkmate(self):
        return self.board.is_checkmate()

    def is_stalemate(self):
        return self.board.is_stalemate()

    def is_check(self):
        return self.board.is_check()

    def is_game_over(self):
        if self.board.is_game_over():
            return self.board.result()
        return None

    def get_best_move(self):
        with self.lock:
            self.stockfish.set_fen_position(self.board.fen())
            return self.stockfish.get_best_move()

    def player_turn(self):
        while not self.board.is_game_over():
            print("Current board:")
            print(self.get_board())
       
            user_action = input("Enter your move in UCI format or 'offer draw' " +
                                    "' or 'accept draw' or 'reject draw' or 'resign' : ")
            match user_action:
                case "offer draw":
                    self.offer_draw(self.game_state, "white")
                    continue
                case "accept draw":
                    self.accept_draw(self.game_state, self.board)
                    break
                case "reject draw":
                    self.reject_draw(self.game_state)
                    continue
                case "resign":
                    self.resign_game(self.game_state)
                    break
            try:
                if not self.make_move(user_action):
                    print("Invalid move. Try again.")
                    continue
            #Stockfish plays
                best_move = self.get_best_move()
                if best_move:
                    print(f"Engine plays: {best_move}")
                    self.make_move(best_move)
            #Check game status
                match self.board.result():
                    case "1-0":
                        print(RESULT_PREFIX + self.board.result())
                        print("Checkmate! You lose.")
                        break
                    case "0-1":
                        print(RESULT_PREFIX + self.board.result())
                        print("Checkmate! You lose.")
                        break
                    case "1/2-1/2":
                        print("Stalemate! It's a draw.")
                        print("Result: " + self.board.result())
                        break
                    case _:
                        if self.is_check():
                            print("Check!")
                        elif self.is_game_over():
                            print("Game over!")
                            print("Result: " + self.board.result())
               
            except ValueError:
                print("Invalid move. Try again.")
                break

    def engine_turn(self):
        self.stockfish.set_fen_position(self.board.fen())
        best_move = self.stockfish.get_best_move()
        if best_move:
            self.board.push_uci(best_move)
            print(self.get_board())
            print(f"Engine plays: {best_move}")
        else:
            print("Engine has no moves. Game over!")
   
    def play_game(self):
        while not self.board.is_game_over():
            if not self.player_turn():
                break
            self.engine_turn()
        print("Game over!")
                 
    def set_depth(self, depth):
        self.stockfish.set_depth(depth)

    def set_position(self, moves):
        self.board.set_fen(moves)


if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
   
        
        