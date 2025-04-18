import streamlit as st
import chess
import chess.svg
from io import StringIO

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

# Render the chessboard as an SVG image
svg = chess.svg.board(st.session_state.board, size=400)
st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)

# Input for entering moves in UCI format
if not st.session_state.game_over:
    move_input = st.text_input("Enter move (e.g., e2e4)", key="move_input")
    if move_input:
        try:
            # Convert the move from UCI format to a chess.Move object
            move = chess.Move.from_uci(move_input)
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
                # Clear the input field by rerunning
                st.rerun()
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
- **Enter Moves**: Type moves in UCI format (e.g., `e2e4` for pawn from e2 to e4) in the text box.
- **Turns**: White moves first, then Black. The current turn is displayed above the board.
- **Game End**: The game ends on checkmate, stalemate, or draw.
- **Reset**: Click "Reset Game" to start a new game.
- **Hosting**: Deploy this app on Streamlit Cloud for others to play!
""")
