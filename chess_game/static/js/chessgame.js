document.addEventListener('DOMContentLoaded', () => {
  const board = Chessboard('board', {
    draggable: true,
    position: 'start',
    pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
    onDrop: (source, target, piece, newPos, oldPos, orientation) => {
      const moveData = {
        gameId : 1,
        source: source,
        target: target,
        piece: piece
      };
    
      move(moveData);
    }
  });

  let token = null;

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

  const move = (moveData) => {
   
    const accessToken = localStorage.getItem('accessToken');
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
      console.log('Server response:', data);
      if(data.error != undefined)
        showMessage(data.error, 'danger');
      else
        showMessage(data.message, 'success');
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage(error.message, 'danger');

    });
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

  const loadGame = (id) => {
    fetch(`http://localhost:8000/api/get-pgn/${id}/`)
    .then(response => response.json())
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  // Reset to the start position
  const resetPosition = () => {
    board.position('start');
  };

  // Apply the FEN position from the input field
  function applyFEN() {
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
});


