
  const getChessInstance = (() => {
    let instance;
    return () => {
      if (!instance) {
        instance = new Chess();
      }
      return instance;
    };
  })();

  const getHistory = (() => {
    let history = [];
    return () => {
      return history;
    };
  })();

  const game = getChessInstance();
  let  board = null
  const VALID_GAME_OVER_REASON = [
    'checkmate', 'stalemate', 'threefold_repetition', 'insufficient_material', 
    'fifty_moves', 'time_control', 'resign', 'agreed_draw'
  ];
  const INITIAL_FEN_WHITE = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  const INITIAL_FEN_BLACK = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1';

  const onDrop = async (...args) => {
    console.log('args', args);
    const [source] = args;
    const sourceSquare = source.source;
    const targetSquare = source.target;
    const piece = source.piece;

    game.load(board.fen());
    board.fen(game.fen());

    console.log('sourceSquare', sourceSquare);
    console.log('targetSquare', targetSquare);
    console.log('piece', piece);
    console.log('orientation', source.orientation);
    console.log('game turn', game.turn());
    console.log('Before board.fen()', board.fen());
    console.log('Before game fen', game.fen());
    console.log('history', getHistory());

    const gameMove = game.move({ from: sourceSquare, to: targetSquare, promotion: 'q' });
    if (gameMove === null) {
      console.log('Invalid move:', sourceSquare, targetSquare);
      
      console.log('Current game state:', game.fen());
      revertLastState();
      console.log('board position after undo', board.position());
      
      // Highlight the target square with a visual signal (e.g., border color change)
      board.setSquareStyle(targetSquare, {
        border: '2px solid red', // Red border to indicate invalid move
        boxShadow: 'inset 0 0 1em red', // Red glow effect});
      });
      setTimeout(() => {
        board.setSquareStyle(targetSquare, { border: '' });
      }, 1000);  // Removes the border after 1 second
 
      return 'snapback';
    }

    //Update the custom history
    saveState();
    
    
    // Log successful move
    console.log('Game history after legal move', game.history());
    console.log('Move made:', gameMove);
    console.log('Game history after move:', game.history());
    console.log('FEN after move:', game.fen());
   
    //If the move is valid, update the board position
    board.position(game.fen());
    console.log('After game fen', game.fen());
    console.log('After board fen', board.fen());
    console.log('game turn', game.turn());

   
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

    saveState();
    console.log('gameId', localStorage.getItem('gameId'));
    console.log('piece', piece);
    const resign = localStorage.getItem('resign');
    if(game.game_over() === true || resign) {
      console.log('game is over');
      showMessage('Game is over', 'danger');
      return false;
    }

    // Prevent dragging if the game is over or it's not the player's turn
    if ((game.turn() === 'w' && piece.piece.startsWith('b')) || 
    (game.turn() === 'b' && piece.piece.startsWith('w'))) {
        console.log('Not your turn');
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
      const history = getHistory();
      saveState();    
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
   
    const $status = $('#status')
    const $fen = $('#fen')
    const $gameId = $('#gameId')

    if(gameStatus === null || gameStatus === undefined) {
      //gameStatus = await loadGame(localStorage.getItem('gameId'));
      return null;
    };

    if(gameStatus.error != null || gameStatus.error != undefined) {
      console.error('Error:', gameStatus.error);
      showMessage(gameStatus.error, 'danger');
      return null;
    }
    //Sync the board with the game
    board.position(gameStatus.board)
    // Set the position using the FEN string
    const success = game.load(gameStatus.board);

    if (success) {
        console.log('FEN successfully loaded!');
        console.log('Current FEN:', game.fen());
    } else {
        console.error('Invalid FEN:', game.fen());
    }

    let status = 'game in progress'

    let moveColor = 'White'
    if (gameStatus.turn === 'b') {
      moveColor = 'Black'
    }

    if(gameStatus.in_resignation) {
      status = 'Game over, ' + moveColor + ' has resigned.'
      console.log('status', status);
      showMessage(status, 'success');
      gameOver(gameStatus.turn, 'resign');
    }
  
    // checkmate?
    if (game.in_checkmate()) {
      status = 'Game over, ' + moveColor + ' is in checkmate.'
      console.log('status', status);
      showMessage(status, 'success');
      gameOver(gameStatus.turn, 'checkmate');
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
      console.log('game over reason', reason);
      showMessage(reason, 'success');
      gameOver('*', reason);
    }  
    // game still on
    else {
      status = 'In progress'
  
      // check?
      if (game.in_check()) {
        status += ', ' + moveColor + ' is in check'
      }
    }

    console.log('status', status);
    console.log('fen', game.fen());
    console.log('gameId', localStorage.getItem('gameId'));
  
    $status.text(status)
    $fen.text(game.fen())
    $gameId.text(localStorage.getItem('gameId'))
 }

 // Function to save the current game state in the custom history
const saveState = () => {
  const customHistory = getHistory();
  customHistory.push({
      fen: game.fen(),
      position: board.position(),
  });
}

// Function to revert to the last valid state
const revertLastState = () => {
  const customHistory = getHistory();
  console.log('customHistory', customHistory);
  if (customHistory.length > 0) {
      const lastState = customHistory.pop();
      console.log('lastState', lastState);
      game.load(lastState.fen); // Revert game state
      setTimeout(() => {
        board.position(lastState.position, true); //Revert board position
    }, 50);
  }
}

 const isOwnPiece = (targetSquare, playerColor) => {
      const piece = game.get(targetSquare);
      return piece && piece.color === playerColor;
  };

 const resign = () => {
    
    const resignedPlayer = game.turn();
    console.log('resignedPlayer', resignedPlayer);
    localStorage.setItem('resign', {'resignedPlayer': resignedPlayer, 
                                        'gameId': localStorage.getItem('gameId'),
                                        'gameOverReason': 'resign'});
    gameOver(resignedPlayer === 'w'? 'b' :'w', 'resign');

  }


 const gameOver = (winner, gameOverReason) => {

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken || accessToken === null || accessToken === undefined) {
      showMessage('Please login to make a move', 'danger');
      return null;
    }
    console.log('gameover accessToken', accessToken);

    if (!VALID_GAME_OVER_REASON.includes(gameOverReason)) {
      console.error('Invalid game over reason:', gameOverReason);
      return;
    }

    console.log('Game over:', winner, gameOverReason);
    // Call the DRF endpoint
    fetch(`http://localhost:8000/api/game-over/${localStorage.getItem('gameId')}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        game_over_date: new Date(),
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
      dropOffBoard: 'snapback', // Snapback invalid moves
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

    // Reset the previous game state
    localStorage.removeItem('resign');

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
      console.log('StartGame game.turn()', game.turn());
      board.position(data.board);
      localStorage.setItem("gameId",data.id);
      const initial_fen = data.turn === 'w' ? INITIAL_FEN_WHITE : INITIAL_FEN_BLACK;
      game.load(initial_fen);
      console.log('game.turn()', game.turn());
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
    setTimeout(() => {
      alertDiv.remove();
    }, 2000);

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
    const loadfen = document.getElementById('loadfen').value;
    console.log('Current FEN:', loadfen);
    const alertBox = document.getElementById('alertBox');
    if (loadfen != '' && loadfen != null && loadfen != undefined) {
      try {
        board.position(loadfen);
        alertBox.innerHTML = '<div class="alert alert-success" role="alert">Position set successfully!</div>';
      } catch (error) {
        alertBox.innerHTML = '<div class="alert alert-danger" role="alert">Invalid FEN string. Please enter a valid FEN.</div>';
      }
    } else {
      alertBox.innerHTML = '<div class="alert alert-warning" role="alert">Please enter a FEN string.</div>';
    }

    alertBox.style.display = 'block';

    setTimeout(() => {
      alertBox.style.display = 'none';
    }, 2000);
  }

  window.applyFEN = applyFEN; 




