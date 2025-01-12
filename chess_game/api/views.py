from django.shortcuts import render

# Create your views here.
import datetime
import chess.pgn
from stockfish import Stockfish
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from .models import ChessGame
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
from .serializers import ChessGameSerializer
from chess_game.utils import is_null_or_empty,make_engine_move,get_dic_value_by_key
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import random
from math import trunc



STOCKFISH_PATH = r"C:\app\stockfish\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(STOCKFISH_PATH)
DRAW_RESULT = "1/2-1/2"
ENGINE_PLAYER = "stockfish"


class  LoginView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_description="User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            },
            required=['username', 'password']
        ),
        responses={
            200: "Login successful",
            400: "Invalid credentials"
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class RefreshTokenView(TokenRefreshView):
    pass

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Logout successful."})
        except Exception as e:
            return Response({"error": "Invalid token."}, status=400)
    
class SecureView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Access a secure endpoint",
        responses={200: "This is a secure endpoint!"}
    )
    def get(self, request):
        return Response({"message": "This is a secure endpoint!"})

class StartGameView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Start a new chess game",
        responses={201: ChessGameSerializer()},
    )
    def post(self, request):
        board = chess.Board()
        game = ChessGame.objects.create(board=board.fen())
        opponent = request.data.get("opponent")
        
        if is_null_or_empty(opponent):
            return Response({"error": "Opponent not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if opponent == "human":
            if random.randint(0, 1) == 0:
                game.player_white = request.user.username
                game.player_black = request.data.get("opponent_user")
            else:
                game.player_white = request.data.get("opponent_user")
                game.player_black = request.user.username
        elif opponent == "engine":
            if random.randint(0, 1) == 0:
                game.player_white = request.user.username
                game.player_black = ENGINE_PLAYER
            else:
                game.player_white = ENGINE_PLAYER
                game.player_black = request.user.username
                game.orientation = "black"
            
        game.game_mode = request.data.get("game_mode")
        game.initial_time = request.data.get("initial_time")
        game.increment = request.data.get("increment")
        game.result = "*" if request.data.get("result") == "" or request.data.get("result") == None else request.data.get("result")
        game.save()
        
        #white player makes the first move
        if game.player_white == ENGINE_PLAYER:
            game.moves = make_engine_move(game, board)
            game.orientation = "black"
            if(game.moves == ""):
                return Response({"error": "Invalid engine move."}, status=status.HTTP_400_BAD_REQUEST)
            game.save()
     
        return Response(ChessGameSerializer(game).data, status=status.HTTP_201_CREATED)
        
class MakeMoveView(APIView):
    permission_classes = [IsAuthenticated]
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
            self.engine_move = ""
            
            if(game.game_over):
                return Response({"error": "Game is over."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not self.moves:
                return Response({"move": "Move not provided."}, status=status.HTTP_400_BAD_REQUEST)
            else:   
                board = chess.Board(game.board)
                if chess.Move.from_uci(self.moves) not in board.legal_moves:
                    return Response({"move": "Invalid move."}, status=status.HTTP_400_BAD_REQUEST)
            
                board.push(chess.Move.from_uci(self.moves))
                game.board = board.fen()
                game.moves += f" {self.moves}"
                
                #Check if the game is over
                self.check_game_status(game, board)
                game.save()
                
                #Get engine move
                board = chess.Board(game.board)
                self.engine_move = make_engine_move(game, board)
                if(self.engine_move == ""):
                    return Response({"error": "Invalid engine move."}, status=status.HTTP_400_BAD_REQUEST)
                
                self.check_game_status(game, board)
                game.save()
                    
                
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def check_game_status(self, game, board):
       
        def set_game_over(result, reason_key):
            game.result = result
            game.game_over = True
            game.game_over_reason = get_dic_value_by_key(game.GAME_OVER_REASON_CHOICES, reason_key)

        def check_and_set_game_over(condition, result, reason_key):
            if condition:
                set_game_over(result, reason_key)

        WON_RESULT = "1-0" if board.turn == chess.BLACK else "0-1"
        check_and_set_game_over(board.is_checkmate(), WON_RESULT, "checkmate")
        check_and_set_game_over(board.is_stalemate(), DRAW_RESULT, "stalemate")
        check_and_set_game_over(board.is_insufficient_material(), DRAW_RESULT, "insufficient_material")
        check_and_set_game_over(board.is_seventyfive_moves(), DRAW_RESULT, "seventyfive_moves")
        check_and_set_game_over(board.is_fivefold_repetition(), DRAW_RESULT, "fivefold_repetition")
        # check_and_set_game_over(board.is_variant_draw(), DRAW_RESULT, "variant_draw")
        # check_and_set_game_over(board.is_variant_mate(), WON_RESULT, "variant_mate")
        # check_and_set_game_over(board.is_variant_loss(), WON_RESULT, "variant_loss")
        # check_and_set_game_over(board.is_variant_win(), WON_RESULT, "variant_win")


class GameOverView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="End the chess game",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': openapi.Schema(type=openapi.TYPE_STRING, description='The result of the game'),
                'game_over_date': openapi.Schema(type=openapi.TYPE_STRING, description='The date when the game ended'),
                'winner': openapi.Schema(type=openapi.TYPE_STRING, description='The winner of the game'),
                'game_over_reason': openapi.Schema(type=openapi.TYPE_STRING, description='The reason the game ended')
            },
        ),
        responses={
            200: ChessGameSerializer(),
            400: "Result not provided",
            404: "Game not found",
            500: "Internal server error"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            result = request.data.get("result")
            game_over_date = request.data.get("game_over_date")
            winner = request.data.get("winner")
            game_over_reason = request.data.get("game_over_reason")
            
            if is_null_or_empty(result):
                return Response({"error": "Result not provided."}, status=status.HTTP_400_BAD_REQUEST)
            
            game.result = result
            game.game_over = True
            game.game_over_date = game_over_date
            game.winner = winner
            game.game_over_reason = get_dic_value_by_key(game.GAME_OVER_REASON_CHOICES, game_over_reason)
            game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResetGameView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Reset the chess game",
        responses={
            200: ChessGameSerializer(),
            404: "Game not found"
        }
    )
    def post(self, request, pk):
        try:
            game = ChessGame.objects.get(pk=pk)
            game.board = chess.Board().fen()
            game.moves = ""
            game.result = ""
            game.game_over = False
            game.game_over_reason = ""
            game.draw_offered_by = None
            game.draw_accepted = False
            game.resign = False
            game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)    
        
    
class OfferDrawView(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
                game.result = DRAW_RESULT
                game.game_over = True
                game.game_over_reason = get_dic_value_by_key(game.GAME_OVER_REASON_CHOICES, "agreed_draw")
                game.save()
                return Response(ChessGameSerializer(game).data)
                
            return Response({"error": "No draw offered."}, status=status.HTTP_400_BAD_REQUEST)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class RejectDrawView(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
            board = chess.Board(game.board)
            game.resign = True
            game.result = "1-0" if board.turn == chess.BLACK else "0-1"
            game.game_over_reason = get_dic_value_by_key(game.GAME_OVER_REASON_CHOICES, "resign")
            game.save()
            return Response(ChessGameSerializer(game).data)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GetGameView(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
            fen = game.initial_fen  
            uci_moves = game.moves
            pgn = self.generate_pgn(fen, uci_moves, game.player_white, game.player_black, game.result, game.event)
            game.pgn = pgn
            game.fen = game.board
            game.save()
            return Response(pgn)
        except ChessGame.DoesNotExist:
            return Response({"error: Game not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"error: An error occurred",ex}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
         
    def generate_pgn(self,fen, uci_moves, player_white, player_black,game_result, game_event):
        """
        Generate a PGN string from an initial FEN and a sequence of UCI moves.

        Args:
            fen (str): The current FEN of the game.
            uci_moves (str): Space-separated UCI moves.
            player_white (str): Name of the White player.
            player_black (str): Name of the Black player.
            game_result (str): Result of the game.
            game_event (str): Event name of the game.

        Returns:
            str: PGN representation of the game.
        """
        # Initialize the board with the starting FEN
        board = chess.Board(fen)

        # Create a PGN game object
        game = chess.pgn.Game()
        game.headers["Event"] = game_event
        game.headers["White"] = player_white
        game.headers["Black"] = player_black
        game.headers["FEN"] = fen
        game.headers["Result"] = game_result  
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["Site"] = "ChessServer"
  
        # Replay the moves on the board and populate the PGN object
        node = game
        for move in uci_moves.split():
            next_node = node.add_variation(chess.Move.from_uci(move))
            board.push_uci(move)
            node = next_node

        node.root().headers["FEN"] = game.board().fen()
    
        # Save the PGN as a string
        pgn_string = node.root().accept(chess.pgn.StringExporter())
        return pgn_string
