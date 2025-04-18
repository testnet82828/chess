import streamlit as st
import chess
import streamlit.components.v1 as components

# Initialize session state for the chess board and game status
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White, False for Black
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'status_message' not in st.session_state:
    st.session_state.status_message = ""
if 'chess_move' not in st.session_state:
    st.session_state.chess_move = None

# Streamlit app title
st.title("Simple Chess Game")

# Display whose turn it is
if not st.session_state.game_over:
    st.write(f"**Turn**: {'White' if st.session_state.player_turn else 'Black'}")

# JavaScript for chessboard.js
chessboard_html = f"""
<link rel="stylesheet" href="https://unpkg.com/chessboard-js@1.0.0/css/chessboard-1.0.0.min.css">
<script src="https://unpkg.com/chessboard-js@1.0.0/js/chessboard-1.0.0.min.js"></script>
<div id="board" style="width: 400px; margin: auto;"></div>
<script>
    var board = Chessboard('board', {{
        position: '{st.session_state.board.fen()}',
        draggable: true,
        onDrop: function(source, target) {{
            var move = source + '-' + target;
            window.Streamlit.setComponentValue(move);
        }}
    }});
</script>
"""

# Render chessboard.js component with a unique key
components.html(chessboard_html, height=450, width=450, key="chessboard")

# Handle moves from the component
move = st.session_state.get("chessboard")
if move and not st.session_state.game_over:
    try:
        # Convert move from chessboard.js format (e.g., "e2-e4") to UCI (e.g., "e2e4")
        move_uci = move.replace("-", "")
        chess_move = chess.Move.from_uci(move_uci)
        if chess_move in st.session_state.board.legal_moves:
            # Apply move
            st.session_state.board.push(chess_move)
            # Switch player turn
            st.session_state.player_turn = not st.session_state.player_turn
            # Check game status
            if st.session_state.board.is_game_over():
                st.session_state.game_over = True
                if st.session_state.board.is_checkmate():
                    winner = "White" if not st.session_state.player_turn else "Black"
                    st.session_state.status_message = f"Checkmate! {winner} wins!"
                elif st.session_state.board.is_stalemate():
                    st.session_state.status_message = "Stalemate! The game is a draw."
                elif st.session_state.board.is_insufficient_material():
                    st.session_state.status_message = "Draw due to insufficient material."
                else:
                    st.session_state.status_message = "Game over: Draw."
            else:
                st.session_state.status_message = ""
            # Clear the move to prevent reprocessing
            st.session_state.chess_move = None
            st.rerun()
        else:
            st.session_state.status_message = "Illegal move! Try again."
            st.session_state.chess_move = None
    except ValueError:
        st.session_state.status_message = "Invalid move format! Try again."
        st.session_state.chess_move = None

# Display game status or error messages
if st.session_state.status_message:
    st.write(st.session_state.status_message)

# Reset game button
if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.player_turn = True
    st.session_state.game_over = False
    st.session_state.status_message = ""
    st.session_state.chess_move = None
    st.rerun()

# Display current board FEN (for debugging)
with st.expander("Board FEN (Debug)"):
    st.write(st.session_state.board.fen())

# Instructions
st.markdown("""
### How to Play
- **Move Pieces**: Click or drag pieces on the board to make moves (e.g., click e2 pawn, then e4 square).
- **Turns**: White moves first, then Black. The current turn is displayed above the board.
- **Game End**: The game ends on checkmate, stalemate, or draw.
- **Reset**: Click "Reset Game" to start a new game.
- **Local Play**: Two players can take turns on the same device (White vs. Black).
""")
