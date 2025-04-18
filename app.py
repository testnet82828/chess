import streamlit as st
import chess
import chess.svg
from stchess import st_chess_board

# Initialize session state for the chess board and game status
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White, False for Black
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'status_message' not in st.session_state:
    st.session_state.status_message = ""

# Streamlit app title
st.title("Multiplayer Chess Game")

# Display whose turn it is
if not st.session_state.game_over:
    st.write(f"**Turn**: {'White' if st.session_state.player_turn else 'Black'}")

# Render the chessboard using streamlit-chess
board_state, move_made, action = st_chess_board(
    fen=st.session_state.board.fen(),
    key="chess_board",
    piece_set="cardinal",  # Optional: choose a piece set (e.g., cardinal, staunty)
    board_size=400  # Adjust board size as needed
)

# Handle moves made on the board
if move_made and not st.session_state.game_over:
    try:
        # Convert the move from UCI format (e.g., "e2e4") to a chess.Move object
        move = chess.Move.from_uci(move_made)
        if move in st.session_state.board.legal_moves:
            # Apply the move to the board
            st.session_state.board.push(move)
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
        else:
            st.session_state.status_message = "Illegal move! Try again."
    except ValueError:
        st.session_state.status_message = "Invalid move format! Try again."

# Display game status or error messages
if st.session_state.status_message:
    st.write(st.session_state.status_message)

# Reset game button
if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.player_turn = True
    st.session_state.game_over = False
    st.session_state.status_message = ""
    st.rerun()

# Display the current board FEN (for debugging or sharing)
with st.expander("Board FEN (Debug)"):
    st.write(st.session_state.board.fen())

# Instructions
st.markdown("""
### How to Play
- **Move Pieces**: Click and drag pieces on the board to make moves.
- **Turns**: White moves first, then Black. The current turn is displayed above the board.
- **Game End**: The game ends on checkmate, stalemate, or draw.
- **Reset**: Click "Reset Game" to start a new game.
- **Hosting**: Deploy this app on Streamlit Cloud for others to play!
""")
