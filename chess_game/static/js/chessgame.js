
  
  
  const  game = new Chess()
  let  board = null
  const $status = $('#status')
  const $fen = $('#fen')
  const $pgn = $('#pgn')
  
  
  const onDrop = (source, target, piece) => {
    const targetSquare = (source?.square || source).target; // Ensure valid target
    const sourceSquare = (source?.square || source).source; // Ensure valid source
    console.log('sourceSquare',sourceSquare);
    console.log('targetSquare', targetSquare);

    //Update Sync the board with the game
    board.move(`${sourceSquare}-${targetSquare}`);

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

    // Check if there's a piece on the source square
    const pieceInfo = game.get(sourceSquare);
    if (!pieceInfo) {
        console.error(`Piece at source square: ${sourceSquare} not found`);
        return 'snapback';
    }
    console.log(`Piece on source square: ${pieceInfo.type} (${pieceInfo.color})`);

    const legalMoves = game.moves({ square: sourceSquare, verbose: true });
    console.log('Legal moves for sourceSquare:', legalMoves);

    const isMoveLegal = legalMoves.some(
        move => move.from === sourceSquare && move.to === targetSquare
    );
    
    console.log('Current game position (FEN):', game.fen());

    // if (!isMoveLegal) {
    //     console.error(`Move from ${sourceSquare} to ${targetSquare} is not legal.`);
    //     return 'snapback';
    // }

    // Check for promotion (optional)
    const isPromotion = pieceInfo.type === 'p' && (
        (targetSquare[1] === '8' && pieceInfo.color === 'w') || 
        (targetSquare[1] === '1' && pieceInfo.color === 'b')
    );

    const movePiece = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: isPromotion ? 'q' : undefined // Promote to queen if needed
    });

    

    if (movePiece === null) {
        console.error(`Invalid move: ${sourceSquare} to ${targetSquare}`);
        return 'snapback';
    }

    console.log(`Move made: ${movePiece.san}`);

    const gameStatus = move(moveData); // Call your move handler
    console.log('Return move:', gameStatus);
    if(gameStatus !== null) {
      updateStatus(gameStatus); // Update the game status
    }
    else
    {
      console.error('Error making move');
      return 'snapback';
    }
};


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
    const chessgame = await loadGame(localStorage.getItem('gameId'));
    if (chessgame !== null && chessgame !== undefined) {
      console.log('Chess game:', chessgame);
      console.log('Piece:', piece);
    } else {
      console.error('Error loading game');
    }
    // do not pick up pieces if the game is over
    if (chessgame.game_over) return false;

    // only pick up pieces for the side to move
    if ((chessgame.turn === 'white' && piece.piece.search(/^b/) !== -1) ||
        (chessgame.turn === 'black' && piece.piece.search(/^w/) !== -1)) {
      console.log('Invalid piece', piece.piece.search(/^b/), piece.piece.search(/^w/));
      return false;
    }

    //update game object status
    game.load(chessgame.board);
    localStorage.setItem('fen', game.fen());
    console.log('onDragStart fen',game.fen());

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
    //If the error get in data (no catched by the try block)
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

  
  const updateStatus = async (gameStatus) => {
   
    if(gameStatus === null || gameStatus === undefined) {
      gameStatus = await loadGame(localStorage.getItem('gameId'));
    };

    console.log('gameStatus:', gameStatus);
    //Sync the board with the game
    board.position(gameStatus.board)
    // Set the position using the FEN string
    const success = game.load(gameStatus.board);

    if (success) {
        console.log('FEN successfully loaded!');
        console.log('Current FEN:', game.fen());
    } else {
        console.error('Invalid FEN:', fen);
    }

    let status = ''

    let moveColor = 'White'
    if (gameStatus.turn === 'black') {
      moveColor = 'Black'
    }
  
    // checkmate?
    if (game.in_checkmate()) {
      status = 'Game over, ' + moveColor + ' is in checkmate.'
    }
  
    // draw?
    else if (game.in_draw()) {
      status = 'Game over, drawn position'
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
    updateStatus()
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
    console.log('accessToken', accessToken);

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
  };


  const move = (moveData) => {
   
    const accessToken = localStorage.getItem('accessToken');
    if(!accessToken) {
      showMessage('Please login to make a move', 'danger');
      return null;
    }
    console.log('accessToken', accessToken);

    // Call the DRF endpoint
    fetch(`http://localhost:8000/api/move/${moveData.gameId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(moveData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('MakeMove server response:', data);
    
      const chessBoardMove = getChessBoardMove(data.moves);
      console.log('chessBoardMove', chessBoardMove);
      return data;
    })
    .catch(error => {
      console.error('Error:', error);
      if(handle401Error(error) === 401) {
        move(moveData);
      }
      showMessage(error.message, 'danger');
    });
  };

  const getChessBoardMove = (move) => {
    const source = move.trim().substring(0, 2);
    const target = move.trim().substring(2, 4);
    return {
      from: source,
      to: target,
      promotion: 'q', // Always promote to queen for example simplicity
      moveCode: `${source}-${target}`
    };
  };
  
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

  const resetGame = () => {
    const gameId = localStorage.getItem('gameId');
    fetch(`http://localhost:8000/api/reset-game/${gameId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`  
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

  window.resetGame = resetGame;

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




