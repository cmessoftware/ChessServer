from django.shortcuts import render

# Create your views here.
import chess
import chess.pgn
from stockfish import Stockfish
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import ChessGame
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
from .serializers import ChessGameSerializer
from io import StringIO



STOCKFISH_PATH = r"C:\app\stockfish\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(STOCKFISH_PATH)


class StartGameView(APIView):
    @swagger_auto_schema(
        operation_description="Start a new chess game",
        responses={201: ChessGameSerializer()},
    )
    def post(self, request):
        board = chess.Board()
        game = ChessGame.objects.create(board=board.fen())
        
        return Response(ChessGameSerializer(game).data, status=status.HTTP_201_CREATED)
        
class MakeMoveView(APIView):
    @swagger_auto_schema(
        operation_description="Make a move in the chess game",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'moves': openapi.Schema(type=openapi.TYPE_STRING, description='The moves chain in UCI format')
            },
            required=['move']
        ),
        responses={
            200: ChessGameSerializer(),
            400: "Invalid move or move not provided",
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            self.moves = request.data.get("moves")
            if not self.moves:
                return Response({"moves": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
            board = chess.Board(game.board)
            if chess.Move.from_uci(self.moves) not in board.legal_moves:
                return Response({"move": "Invalid move."}, status=status.HTTP_400_BAD_REQUEST)
            board.push(chess.Move.from_uci(self.moves))
            game.board = board.fen()
            moves = self.add_move(self.moves)
            game.moves = self.moves
            game.save()
            #Get stockfish move
            stockfish.set_fen_position(board.fen())
            stockfish_move = stockfish.get_best_move()
            if stockfish_move:
                board.push(chess.Move.from_uci(stockfish_move))
                game.board = board.fen()
                game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def add_move(self, uci_move):
        if not self.moves:
            self.moves = uci_move
        else:
            self.moves += f" {uci_move}"
        return self.moves
        
class OfferDrawView(APIView):
    @swagger_auto_schema(
        operation_description="Offer a draw in the chess game",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player': openapi.Schema(type=openapi.TYPE_STRING, description='The player offering the draw')
            },
            required=['player']
        ),
        responses={
            200: ChessGameSerializer(),
            400: "Draw already offered or player not provided",
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            player = request.data.get("player")
            if game.draw_offered_by:
                return Response("error: Draw already offered.", status=status.HTTP_400_BAD_REQUEST)
            game.draw_offered_by = player
            game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
class AcceptDrawView(APIView):
    @swagger_auto_schema(
        operation_description="Accept a draw in the chess game",
        responses={
            200: ChessGameSerializer(),
            400: "No draw offered",
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            if game.draw_offered_by:
                game.draw_accepted = True
                game.result = "1/2-1/2"
                game.save()
                return Response(ChessGameSerializer(game).data)
                
            return Response({"error": "No draw offered."}, status=status.HTTP_400_BAD_REQUEST)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class RejectDrawView(APIView):
    @swagger_auto_schema(
        operation_description="Reject a draw offer in the chess game",
        responses={
            200: ChessGameSerializer(),
            400: "No draw offered",
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            if game.draw_offered_by:
                game.draw_offered_by = None
                game.save()
                return Response(ChessGameSerializer(game).data)
            return Response({"error": "No draw offered."}, status=status.HTTP_400_BAD_REQUEST)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
class ResignGameView(APIView):
    @swagger_auto_schema(
        operation_description="Resign from the chess game",
        responses={
            200: ChessGameSerializer(),
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            game.resign = True
            game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GameCurrentStateView(APIView):
    @swagger_auto_schema(
        operation_description="Get the current state of the chess game",
        responses={
            200: ChessGameSerializer(),
            404: "Game not found"
        }
    )
    def get(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GamePgnView(APIView):
    @swagger_auto_schema(
        operation_description="Get the PGN of the chess game",
        responses={
            200: "The PGN of the game",
            404: "Game not found"
        }
    )
    def get(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            initial_fen = game.initial_fen
            uci_moves = game.moves
            pgn = self.generate_pgn(initial_fen, uci_moves, player1="Alice", player2="Bob")
            print(f'PGN: \n {pgn}')
            return Response(pgn)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def generate_pgn(self,fen, uci_moves, player1="Player1", player2="Player2",result="*", game_event="Example"):
        """
        Generate a PGN string from an initial FEN and a sequence of UCI moves.

        Args:
            fen (str): The starting FEN of the game.
            uci_moves (str): Space-separated UCI moves.
            player1 (str): Name of Player 1 (White).
            player2 (str): Name of Player 2 (Black).

        Returns:
            str: PGN representation of the game.
        """
        # Initialize the board with the starting FEN
        board = chess.Board(fen)

        # Create a PGN game object
        game = chess.pgn.Game()
        game.headers["Event"] = game_event
        game.headers["White"] = player1
        game.headers["Black"] = player2
        game.headers["FEN"] = fen
        game.headers["Result"] = result  # Replace with actual result later
  
        # Replay the moves on the board and populate the PGN object
        node = game
        for move in uci_moves.split():
            next_node = node.add_variation(chess.Move.from_uci(move))
            board.push_uci(move)
            node = next_node

        # Save the PGN as a string
        pgn_string = node.root().accept(chess.pgn.StringExporter())
        return pgn_string
