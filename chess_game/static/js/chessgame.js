
  
  const  game = new Chess()
  let  board = null
  const $status = $('#status')
  const $fen = $('#fen')
  const $pgn = $('#pgn')
  const VALID_GAME_OVER_REASON = [
    'checkmate', 'stalemate', 'threefold_repetition', 'insufficient_material', 
    'fifty_moves', 'time_control', 'resign', 'agreed_draw'
  ];
  const onDrop = async (source, piece) => {
    const targetSquare = (source?.square || source).target; // Ensure valid target
    const sourceSquare = (source?.square || source).source; // Ensure valid source
    console.log('sourceSquare', sourceSquare);
    console.log('targetSquare', targetSquare);

    // Set the position using the FEN string
    console.log('Before board.fen()', board.fen());
    console.log('Before game fen', game.fen());
    // Update Sync the board with the game

    const gameMove = game.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    if (gameMove === null) {
      console.log('Invalid move:', sourceSquare, targetSquare);
      return 'snapback';
    }
    //If the move is valid, update the board position
    board.position(game.fen());
    console.log('After game fen', game.fen());
    console.log('After board fen', board.fen());


    //if the game is over, do not allow any moves
    if (game.game_over()) 
    {
      console.log('game is over');
      return 'snapback';
    }
    
    const onDragStartFen = localStorage.getItem('fen');
    console.log('onDragStartFen', onDragStartFen);
    console.log('game fen', game.fen());
    console.log('chessboard.board', board.fen());

   
    if (!(source?.square || source) || !(source?.square || source).target) {
      console.error('Invalid source or target:', (source?.square || source), targetSquare);
      return 'snapback';
    }

    const moveData = {
      gameId: localStorage.getItem('gameId'),
      source: sourceSquare,
      target: targetSquare,
      piece: piece,
      moves: `${sourceSquare}${targetSquare}`
    };

    console.log('Move data:', moveData);
    console.log(`Trying move ${moveData.moves}`);
    console.log(`Current turn: ${game.turn()}`);
    console.log('Current game position (FEN):', game.fen());

    move(moveData)
      .then(data => {
        console.log('Move server response:', data);
        updateStatus(data);
      })
      .catch(error => {
        console.error('Error:', error);
        showMessage(error.message, 'danger');
      });
};  // end of onDrop


  const onDragMove = (newLocation, oldLocation, source, piece, position, orientation) => {
    console.log('New location:', newLocation);
    console.log('Old location:', oldLocation);
    console.log('Source:', source);
    console.log('Piece:', piece);
    console.log('Position:', position);
    console.log('Orientation:', orientation);
  };


  const onDragStart = async (piece) => {
    console.log('gameId', localStorage.getItem('gameId'));
    console.log('piece', piece);

    if(game.game_over() === true) {
      console.log('game is over');
      return false;
    }

    // Prevent dragging if the game is over or it's not the player's turn
    if ((game.turn() === 'w' && piece.piece.startsWith('b')) || 
    (game.turn() === 'b' && piece.piece.startsWith('w'))) {
        return false;
    }
  };

  const handleTokenError = (error) => {
    if(error.status === 401)
    {
        const refreshToken = localStorage.getItem('refreshToken');
        if(refreshToken) {
          const newAccessToken = refreshAccessToken(refreshToken);
          localStorage.setItem('accessToken', newAccessToken);
        }
    }
    //If the error gets in data (not caught by the try block)
    if(error.code === "token_not_valid")
    {
      const refreshToken = localStorage.getItem('refreshToken');
      if(refreshToken) {
        const newAccessToken = refreshAccessToken(refreshToken);
        localStorage.setItem('accessToken', newAccessToken);
      }
    }
    return error.status;
  };

  const move = async (moveData) => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      showMessage('Please login to make a move', 'danger');
      return null;
    }
    console.log('accessToken', accessToken);
  
    try {
      const response = await fetch(`http://localhost:8000/api/move/${moveData.gameId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(moveData)
      });
      const data = await response.json();
      console.log('MakeMove server response:', data);
      console.log('data', data);
      return data;
    } catch (error) {
      console.error('Error:', error);
      if (handle401Error(error) === 401) {
        return move(moveData);
      }
      showMessage(error.message, 'danger');
      return null;
    }
  };

  
  const updateStatus = async (gameStatus) => {
   
    if(gameStatus === null || gameStatus === undefined) {
      //gameStatus = await loadGame(localStorage.getItem('gameId'));
      return null;
    };

    console.log('gameStatus:', gameStatus);
    //Sync the board with the game
    board.position(gameStatus.board,'slow')
    // Set the position using the FEN string
    const success = game.load(gameStatus.board);

    if (success) {
        console.log('FEN successfully loaded!');
        console.log('Current FEN:', game.fen());
    } else {
        console.error('Invalid FEN:', game.fen());
    }

    let status = ''

    let moveColor = 'White'
    if (gameStatus.turn === 'black') {
      moveColor = 'Black'
    }
  
    // checkmate?
    if (game.in_checkmate()) {
      status = 'Game over, ' + moveColor + ' is in checkmate.'
      gameOver(new Date(), gameStatus.turn, 'checkmate');
    }
  
    // draw?
    else if (game.in_draw()) {
      status = 'Game over, drawn position'
      let reason = "";

      switch (true) {
        case game.in_stalemate():
          reason = 'stalemate';
          break;
        case game.in_threefold_repetition():
          reason = 'threefold_repetition';
          break;
        case game.insufficient_material():
          reason = 'insufficient_material';
          break;
        case game.in_fifty_moves():
          reason = 'fifty_moves';
          break;
        case game.in_time_control():
          reason = 'time_control';
          break;
        case game.draw_offer():
          reason = 'draw_offer';
          break;
        case game.resign():
          reason = 'resign';
          break;
        case game.agreed_draw():
          reason = 'agreed_draw';
          break;
        default:
          reason = 'unknown';
      }
      gameOver(new Date(), '*', reason);
    }  
    // game still on
    else {
      status = moveColor + ' to move'
  
      // check?
      if (game.in_check()) {
        status += ', ' + moveColor + ' is in check'
      }
    }
  
    $status.html(status)
    $fen.html(game.fen())
    $pgn.html(game.pgn())
 }

 const isOwnPiece = (targetSquare, playerColor) => {
      const piece = game.get(targetSquare);
      return piece && piece.color === playerColor;
  };


 const gameOver = (gameOverDate, winner, endType) => {

    if (!VALID_END_GAME.includes(endType)) {
      console.error('Invalid end type:', endType);
      return;
    }

    console.log('Game over:', gameOverDate, winner, gameOverReason);
    // Call the DRF endpoint
    fetch('http://localhost:8000/api/game-over/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      },
      body: JSON.stringify({
        gameId: localStorage.getItem('gameId'),
        game_over_date: gameOverDate,
        winner: winner,
        game_over_reason: gameOverReason
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };


  // update the board position after the piece snap
  // for castling, en passant, pawn promotion
  const onSnapEnd = () => {
    board.position(game.fen())
  }

  document.addEventListener('DOMContentLoaded', () => {
    const config = {
      draggable: true,
      position: 'start',
      onDragStart: onDragStart,
      onDrop: onDrop,
      onSnapEnd: onSnapEnd,
      onDragMove: onDragMove,
      pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    }

    board = Chessboard2('#board', config);
    //updateStatus()
  });

  const login = (username, password) => {
    const userData = {
      username: username,
      password: password
    };
    // Call the DRF endpoint
    fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      localStorage.setItem('accessToken', data.access);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  window.login = login;

  const refreshAccessToken = async (refreshToken) => {
    try {
        const response = await axios.post('http://localhost:8000/api/login/refresh/', {
            refresh: refreshToken,
        });
        return response.data.access; // New access token
    } catch (error) {
        console.error('Failed to refresh token', error.response?.data || error.message);
    }
 }

 
 const resetGame = () => {

    const accessToken = localStorage.getItem('accessToken');
    if(!accessToken) {
      showMessage('Please login to start game', 'danger');
    }
    console.log('resetGame accessToken', accessToken);
    const gameId = localStorage.getItem('gameId');
    fetch(`http://localhost:8000/api/reset-game/${gameId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body : JSON.stringify({gameId: gameId})
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      board.position(data.position);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };


 const updateAccessToken = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if(refreshToken) {
      const newAccessToken = await refreshAccessToken(refreshToken);
      localStorage.setItem('accessToken', newAccessToken);
    }
    else {
      console.error('No refresh token found');
    }
  }


  const startGame = () => {

    const accessToken = localStorage.getItem('accessToken');
    if(!accessToken) {
      showMessage('Please login to start game', 'danger');
    }
    console.log('startGame accessToken', accessToken);

    game.reset();
    board.position(game.fen());

    const startData = {
      position: 'start',
      game_type: 'standard',
      game_mode: 'rapid',
      initial_time: 10,
      increment: 5,
      opponent: 'engine', // or 'human' for human vs human (not implemented yet)
      opponent_user: "player1"
    };

    fetch('http://localhost:8000/api/start-game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      },
      body: JSON.stringify(startData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('StartGame server response:', data);
      handleTokenError(data);
      board.orientation(data.orientation);
      board.position(data.board);
      localStorage.setItem("gameId",data.id);
    })
    .catch(error => {
      console.error('Error:', error);
      if(handle401Error(error) === 401) {
        startGame();
      }
      showMessage(error.message, 'danger');
    }); 


    

  const getChessBoardMove = (movement) => {
    const source = movement.trim().substring(0, 2);
    const target = movement.trim().substring(2, 4);
    return {
      from: source,
      to: target,
      promotion: 'q', // Always promote to queen for example simplicity
      moveCode: `${source}-${target}`
    };
  }};
  
  const handle401Error = (error) => {
    if(error.status === 401)
    {
        const refreshToken = localStorage.getItem('refreshToken');
        if(refreshToken) {
          const newAccessToken = refreshAccessToken(refreshToken);
          localStorage.setItem('accessToken', newAccessToken);
        }
    }
    return error.status;
  };

  const showMessage = (message, type) => {
    const alertDiv = document.createElement('div');
    if(type === 'danger') 
      alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    else if(type === 'success')
      alertDiv.className = 'alert alert-success alert-dismissible fade show';
    else
      alertDiv.className = 'alert alert-warning alert-dismissible fade show';

    alertDiv.role = 'alert';
    alertDiv.innerHTML = `Error: ${message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>`;
    document.getElementById('alertBox').appendChild(alertDiv);
  }

  const loadGame = async (id) => {

    if(id === null || id === undefined) {
      console.error('Invalid game id:', id);
      return null;
    }
    const accessToken = localStorage.getItem('accessToken');
    if(!accessToken) {
      showMessage('Please login to make a move', 'danger');
      return null;
    }
    console.log('loadGame accessToken', accessToken);

    try {
      const response = await fetch(`http://localhost:8000/api/get-game/${id}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        }
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  };

  window.loadGame = loadGame;

  // Reset to the start position
  const resetPosition = () => {
    board.position('start');
  };

  window.resetPosition = resetPosition;

 
  // Apply the FEN position from the input field
  const applyFEN = () => {
    const fen = document.getElementById('fen').value.trim();
    const alertBox = document.getElementById('alertBox');
    if (fen) {
      try {
        board.position(fen);
        alertBox.innerHTML = '<div class="alert alert-success" role="alert">Position set successfully!</div>';
      } catch (error) {
        alertBox.innerHTML = '<div class="alert alert-danger" role="alert">Invalid FEN string. Please enter a valid FEN.</div>';
      }
    } else {
      alertBox.innerHTML = '<div class="alert alert-warning" role="alert">Please enter a FEN string.</div>';
    }
  }

  window.applyFEN = applyFEN; 




