import chess
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import ChessGame
from chess.svg import board

class ChessGameTests(APITestCase):
    def test_start_game(self):
        url = reverse('start-game')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('board', response.data)

    def test_make_move(self):
        game = ChessGame.objects.create(board=chess.Board().fen())
        url = reverse('make-move', args=[game.id])
        response = self.client.post(url, {'move': 'e2e4'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('board', response.data)
        current_game = ChessGame.objects.get(id=game.id)
        self.assertEqual(current_game.board, response.data['board'])

    def test_offer_draw(self):
        game = ChessGame.objects.create(board=chess.Board().fen())
        url = reverse('offer-draw', args=[game.id])
        response = self.client.post(url, {'player': 'white'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('draw_offered_by', response.data)

    def test_accept_draw(self):
        game = ChessGame.objects.create(board=chess.Board().fen(), draw_offered_by='white')
        url = reverse('accept-draw', args=[game.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], '1/2-1/2')

    def test_reject_draw(self):
        game = ChessGame.objects.create(board=chess.Board().fen(), draw_offered_by='white')
        url = reverse('reject-draw', args=[game.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['draw_offered_by'])

    def test_resign_game(self):
        game = ChessGame.objects.create(board=chess.Board().fen())
        url = reverse('resign-game', args=[game.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['resign'])

    def test_get_game(self):
        game = ChessGame.objects.create(board=chess.Board().fen())
        url = reverse('get-game', args=[game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Board: " ,board(chess.Board(game.board)))
        self.assertIn('board', response.data)
        
    def test_get_pgn(self):
        game = ChessGame.objects.create(board=chess.Board().fen())
        url = reverse('get-pgn', args=[game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("response.data", response.data)
        self.assertIn(game.pgn, response.data)