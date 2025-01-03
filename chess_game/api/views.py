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



STOCKFISH_PATH = r"C:\app\stockfish\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(STOCKFISH_PATH)
DRAW_RESULT = "1/2-1/2"


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
        player_white = request.data.get("player_white")
        player_black = request.data.get("player_black")
        if(player_white.strip() and player_black.strip()):
            raise serializers.ValidationError("Player White and Player Black fields cannot be set simultaneously.")
        
        if(not is_null_or_empty(request.data.get("player_white"))):
            game.player_white = request.data.get("player_white")
            game.player_black = "Chess Engine"
        elif(not is_null_or_empty(request.data.get("player_black"))):
            game.player_black = request.data.get("player_black")
            game.player_white = "Chess Engine"
            board = chess.Board(game.board)
            make_engine_move(game, board)  #The engine will make the first move
        else:
            raise serializers.ValidationError("Player White or Player Black field cannot be empty.")   
            
        game.game_mode = request.data.get("game_mode")
        game.initial_time = request.data.get("initial_time")
        game.increment = request.data.get("increment")
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
                if(not make_engine_move(game, board)):
                    return Response({"error": "Invalid engine move."}, status=status.HTTP_400_BAD_REQUEST)
                    
                
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
        check_and_set_game_over(board.is_variant_draw(), DRAW_RESULT, "variant_draw")
        check_and_set_game_over(board.is_variant_mate(), WON_RESULT, "variant_mate")
        check_and_set_game_over(board.is_variant_loss(), WON_RESULT, "variant_loss")
        check_and_set_game_over(board.is_variant_win(), WON_RESULT, "variant_win")

    
        
    
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
        
class GameCurrentStateView(APIView):
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
