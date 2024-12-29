import unittest
import chess
from chess_game1 import ChessGame

class TestChessGame(unittest.TestCase):

    def setUp(self):
        self.game = ChessGame()

    def test_initial_board(self):
        self.assertEqual(self.game.get_fen(), chess.Board().fen())

    def test_make_move(self):
        self.assertTrue(self.game.make_move("e2e4"))
        print(self.game.get_fen())
        self.assertEqual(self.game.get_fen(), "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    def test_invalid_move(self):
        self.assertFalse(self.game.make_move("e2e5"))

    def test_offer_draw(self):
        self.game.offer_draw(self.game.game_state, "white")
        self.assertEqual(self.game.game_state["draw_offered_by"], "white")

    def test_accept_draw(self):
        self.game.offer_draw(self.game.game_state, "white")
        self.assertTrue(self.game.accept_draw(self.game.game_state, self.game.board))
        self.assertTrue(self.game.game_state["draw_accepted"])

    def test_reject_draw(self):
        self.game.offer_draw(self.game.game_state, "white")
        self.assertTrue(self.game.reject_draw(self.game.game_state))
        self.assertIsNone(self.game.game_state["draw_offered_by"])

    def test_resign_game(self):
        self.game.resign_game(self.game.game_state)
        self.assertTrue(self.game.game_state["dismissed"])

    def test_is_checkmate(self):
        self.game.set_position("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertFalse(self.game.is_checkmate())

    def test_is_stalemate(self):
        self.game.set_position("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertTrue(self.game.is_stalemate())

    def test_is_check(self):
        self.game.set_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertFalse(self.game.is_check())

    def test_is_game_over(self):
        self.game.set_position("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertIsNotNone(self.game.is_game_over())

    def test_get_best_move(self):
        self.game.make_move("e2e4")
        best_move = self.game.get_best_move()
        self.assertIsNotNone(best_move)

if __name__ == "__main__":
    unittest.main()