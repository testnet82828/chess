import streamlit as st
import chess

# Initialize session state for the chess board and game status
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True  # True for White, False for Black
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'status_message' not in st.session_state:
    st.session_state.status_message = ""
if 'last_move' not in st.session_state:
    st.session_state.last_move = None

# Streamlit app title
st.title("Simple Chess Game")

# Display whose turn it is
if not st.session_state.game_over:
    st.write(f"**Turn**: {'White' if st.session_state.player_turn else 'Black'}")

# HTML and JavaScript for canvas-based chessboard
chessboard_html = f"""
<canvas id="chessboard" width="400" height="400" style="border: 1px solid black; margin: auto; display: block;"></canvas>
<input type="hidden" id="move-input" value="">
<div id="error-message" style="color: red; text-align: center;"></div>
<script>
    try {{
        const canvas = document.getElementById('chessboard');
        const ctx = canvas.getContext('2d');
        const size = 400;
        const squareSize = size / 8;
        let selectedSquare = null;

        // Piece symbols (simplified for display)
        const pieces = {{
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }};

        // FEN to board array
        const fen = '{st.session_state.board.fen()}';
        const board = fen.split(' ')[0].split('/').map(row => 
            row.replace(/(\d)/g, num => '.'.repeat(num)).split('')
        );

        // Draw the board
        function drawBoard() {{
            ctx.clearRect(0, 0, size, size);
            for (let row = 0; row < 8; row++) {{
                for (let col = 0; col < 8; col++) {{
                    ctx.fillStyle = (row + col) % 2 === 0 ? '#eeeed2' : '#769656';
                    ctx.fillRect(col * squareSize, row * squareSize, squareSize, squareSize);
                    const piece = board[row][col];
                    if (piece !== '.') {{
                        ctx.fillStyle = 'black';
                        ctx.font = '30px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(pieces[piece] || '', (col + 0.5) * squareSize, (row + 0.5) * squareSize);
                    }}
                }}
            }}
            if (selectedSquare) {{
                ctx.strokeStyle = 'red';
                ctx.lineWidth = 3;
                ctx.strokeRect(selectedSquare.col * squareSize, selectedSquare.row * squareSize, squareSize, squareSize);
            }}
        }}

        // Convert coordinates to square (e.g., {row: 6, col: 4} to 'e2')
        function squareToNotation(row, col) {{
            return String.fromCharCode(97 + col) + (8 - row);
        }}

        // Handle clicks or touches
        function handleInteraction(x, y) {{
            const col = Math.floor(x / squareSize);
            const row = Math.floor(y / squareSize);
            if (!selectedSquare) {{
                if (board[row][col] !== '.') {{
                    selectedSquare = {{ row, col }};
                    drawBoard();
                }}
            }} else {{
                const move = squareToNotation(selectedSquare.row, selectedSquare.col) + '-' + squareToNotation(row, col);
                document.getElementById('move-input').value = move;
                selectedSquare = null;
                drawBoard();
                // Trigger Streamlit input change
                const input = document.getElementById('move-input');
                const event = new Event('input', {{ bubbles: true }});
                input.dispatchEvent(event);
            }}
        }}

        // Mouse click handler
        canvas.addEventListener('click', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            handleInteraction(x, y);
        }});

        // Touch handler
        canvas.addEventListener('touchstart', (e) => {{
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const x = e.touches[0].clientX - rect.left;
            const y = e.touches[0].clientY - rect.top;
            handleInteraction(x, y);
        }});

        // Initial draw
        drawBoard();
        document.getElementById('error-message').innerText = '';
    }} catch (e) {{
        document.getElementById('error-message').innerText = 'Error loading chessboard: ' + e.message;
        console.error('Canvas error:', e);
    }}
</script>
<style>
    #move-input {{ display: none; }}
</style>
"""

# Render chessboard
st.markdown(chessboard_html, unsafe_allow_html=True)

# Hidden input to capture moves
move_input = st.text_input("Move", key="move_input", value="", label_visibility="collapsed")

# Handle moves
if move_input and not st.session_state.game_over and move_input != st.session_state.last_move:
    try:
        # Convert move from canvas format (e.g., "e2-e4") to UCI (e.g., "e2e4")
        move_uci = move_input.replace("-", "")
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
            # Store the move to prevent reprocessing
            st.session_state.last_move = move_input
            st.rerun()
        else:
            st.session_state.status_message = "Illegal move! Try again."
            st.session_state.last_move = move_input
    except ValueError:
        st.session_state.status_message = "Invalid move format! Try again."
        st.session_state.last_move = move_input

# Display game status or error messages
if st.session_state.status_message:
    st.write(st.session_state.status_message)

# Reset game button
if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.player_turn = True
    st.session_state.game_over = False
    st.session_state.status_message = ""
    st.session_state.last_move = None
    st.rerun()

# Display current board FEN (for debugging)
with st.expander("Board FEN (Debug)"):
    st.write(st.session_state.board.fen())

# Instructions
st.markdown("""
### How to Play
- **Move Pieces**: Tap or click a piece to select it (highlighted with a red border), then tap or click the destination square to move. On touch devices, you can also drag pieces.
- **Turns**: White moves first, then Black. The current turn is displayed above the board.
- **Game End**: The game ends on checkmate, stalemate, or draw.
- **Reset**: Click "Reset Game" to start a new game.
- **Local Play**: Two players can take turns on the same device (White vs. Black).
- **Troubleshooting**: If the board doesn't display, check the browser console (F12 → Console) for errors and report them.
""")
