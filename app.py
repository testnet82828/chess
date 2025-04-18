import streamlit as st
import chess
import chess.svg
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import urllib.parse
import uuid
import time
import json

# Initialize Firebase (only once)
if not firebase_admin._apps:
    # Use Streamlit secrets for Firebase credentials
    firebase_creds = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["firebase"]["database_url"]
    })

# Get game ID from URL query parameters
query_params = st.query_params
game_id = query_params.get("game_id", str(uuid.uuid4()))

# Initialize game in Firebase if it doesn't exist
game_ref = db.reference(f'games/{game_id}')
if not game_ref.get():
    game_ref.set({
        'fen': chess.Board().fen(),
        'player_turn': True,  # True for White, False for Black
        'game_over': False,
        'status_message': '',
        'last_updated': time.time()
    })

# Streamlit app title
st.title("Multiplayer Chess Game")

# Display game link
game_url = f"{st.secrets['app']['base_url']}?game_id={game_id}"
st.markdown(f"**Share this link to play with a friend:** [Join Game]({game_url})")

# Read game state from Firebase
game_state = game_ref.get()
board = chess.Board(game_state['fen'])
player_turn = game_state['player_turn']
game_over = game_state['game_over']
status_message = game_state['status_message']

# Display whose turn it is
if not game_over:
    st.write(f"**Turn**: {'White' if player_turn else 'Black'}")

# JavaScript for chessboard.js
chessboard_html = f"""
<link rel="stylesheet" href="https://unpkg.com/chessboard-js@1.0.0/css/chessboard-1.0.0.min.css">
<script src="https://unpkg.com/chessboard-js@1.0.0/js/chessboard-1.0.0.min.js"></script>
<div id="board" style="width: 400px; margin: auto;"></div>
<script>
    var board = Chessboard('board', {{
        position: '{board.fen()}',
        draggable: true,
        onDrop: function(source, target) {{
            var move = source + '-' + target;
            window.Streamlit.setComponentValue(move);
        }}
    }});
</script>
"""

# Render chessboard.js component
move = components.html(chessboard_html, height=450, width=450)

# Handle moves
if move and not game_over:
    try:
        # Convert move from chessboard.js format (e.g., "e2-e4") to UCI (e.g., "e2e4")
        move_uci = move.replace("-", "")
        chess_move = chess.Move.from_uci(move_uci)
        if chess_move in board.legal_moves:
            # Apply move and update Firebase
            board.push(chess_move)
            game_ref.update({
                'fen': board.fen(),
                'player_turn': not player_turn,
                'last_updated': time.time()
            })
            # Check game status
            if board.is_game_over():
                game_ref.update({
                    'game_over': True,
                    'status_message': (
                        f"Checkmate! {'White' if not player_turn else 'Black'} wins!" if board.is_checkmate() else
                        "Stalemate! The game is a draw." if board.is_stalemate() else
                        "Draw due to insufficient material." if board.is_insufficient_material() else
                        "Game over: Draw."
                    ),
                    'last_updated': time.time()
                })
            else:
                game_ref.update({'status_message': '', 'last_updated': time.time()})
            st.rerun()
        else:
            game_ref.update({'status_message': "Illegal move! Try again.", 'last_updated': time.time()})
    except ValueError:
        game_ref.update({'status_message': "Invalid move format! Try again.", 'last_updated': time.time()})

# Display game status or error messages
if status_message:
    st.write(status_message)

# Reset game button
if st.button("Reset Game"):
    game_ref.set({
        'fen': chess.Board().fen(),
        'player_turn': True,
        'game_over': False,
        'status_message': '',
        'last_updated': time.time()
    })
    st.rerun()

# Display current board FEN (for debugging)
with st.expander("Board FEN (Debug)"):
    st.write(board.fen())

# Poll Firebase for updates
st.markdown(
    """
    <script>
        setInterval(function() {
            window.location.reload();
        }, 3000);
    </script>
    """,
    unsafe_allow_html=True
)

# Instructions
st.markdown("""
### How to Play
- **Move Pieces**: Click or drag pieces on the board to make moves.
- **Multiplayer**: Share the game link with a friend to play together. One player is White, the other is Black.
- **Turns**: White moves first, then Black. The current turn is displayed above the board.
- **Game End**: The game ends on checkmate, stalemate, or draw.
- **Reset**: Click "Reset Game" to start a new game.
- **Hosting**: Deployed on Streamlit Cloud with Firebase for real-time multiplayer.
""")
