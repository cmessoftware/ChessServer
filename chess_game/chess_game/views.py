from django.shortcuts import render

def chessboard_view(request):
    return render(request, 'chessboard.html')