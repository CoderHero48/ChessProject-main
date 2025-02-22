import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
import time
import chessengine as ChessEngine

BOARD_WIDTH = BOARD_HEIGHT = 512
DIMENSION = 8  # Changed from 9 to 8 to match chess board dimensions
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
IMAGES = {}

class ChessUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.game_state = ChessEngine.GameState()
        self.valid_moves = self.game_state.getValidMoves()
        self.state = {"selected": (), "clicks": []}
        self.player_time = 600  # 10 minutes in seconds
        self.opponent_time = 600  # 10 minutes in seconds
        self.timer_running = False
        self.last_time_update = time.time()
        self.move_log = []
        self.move_index = -1
        self.first_move_made = False  # Track if the first move has been made

        # Create canvas
        self.canvas = tk.Canvas(root, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        self.canvas.pack()

        # Load images and initialize board
        if self.loadImages():
            self.drawBoard()
            self.drawPieces(self.game_state.board)
            self.canvas.bind("<Button-1>", lambda event: self.onSquareClick(event))
        else:
            self.root.destroy()
            return

        # Timer labels
        self.player_time_label = tk.Label(root, text="Player Time: 10:00", font=("Arial", 12))
        self.player_time_label.pack(side=tk.LEFT)
        self.opponent_time_label = tk.Label(root, text="Opponent Time: 10:00", font=("Arial", 12))
        self.opponent_time_label.pack(side=tk.RIGHT)

        # Buttons
        self.new_game_button = tk.Button(root, text="New Game", command=self.newGame)
        self.new_game_button.pack(side=tk.TOP)
        self.undo_button = tk.Button(root, text="Undo", command=self.undoMove)
        self.undo_button.pack(side=tk.TOP)
        self.redo_button = tk.Button(root, text="Redo", command=self.redoMove)
        self.redo_button.pack(side=tk.TOP)

    def loadImages(self):
        """
        Initialize a global dictionary of images with error handling.
        """
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        try:
            # Use Path for cross-platform compatibility
            image_path = Path("C:/Users/Divya/Documents/ChessProject-main/ChessPractice-main/index/images")
            for piece in pieces:
                img_path = image_path / f"{piece}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    img = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.LANCZOS)
                    IMAGES[piece] = ImageTk.PhotoImage(img)
                else:
                    raise FileNotFoundError(f"Image not found: {img_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chess pieces: {str(e)}")
            return False
        return True

    def drawBoard(self):
        """
        Draw the chessboard on the canvas.
        """
        colors = ["#f0d9b5", "#b58863"]  # Light and dark squares
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(
                    col * SQUARE_SIZE, row * SQUARE_SIZE,
                    (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                    fill=color, outline=""
                )

    def drawPieces(self, board):
        """
        Draw the chess pieces on the board with error handling.
        """
        self.canvas.delete("pieces")
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = board[row][col]
                if piece != "--" and piece in IMAGES:
                    self.canvas.create_image(
                        col * SQUARE_SIZE, row * SQUARE_SIZE,
                        image=IMAGES[piece],
                        anchor="nw",
                        tags="pieces"
                    )

    def highlightSquares(self, selected_square):
        """
        Highlight selected squares and valid moves with improved visibility.
        """
        if selected_square:
            row, col = selected_square
            if self.game_state.board[row][col][0] == ('w' if self.game_state.white_to_move else 'b'):
                # Highlight selected square
                self.canvas.create_rectangle(
                    col * SQUARE_SIZE, row * SQUARE_SIZE,
                    (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                    outline="#0096FF", width=3  # Brighter blue, thicker outline
                )
                # Highlight valid moves
                for move in self.valid_moves:
                    if move.start_row == row and move.start_col == col:
                        self.canvas.create_rectangle(
                            move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE,
                            (move.end_col + 1) * SQUARE_SIZE, (move.end_row + 1) * SQUARE_SIZE,
                            outline="#FFD700", width=3  # Brighter yellow, thicker outline
                        )

    def onSquareClick(self, event):
        """
        Handle clicks on the chessboard with improved move validation.
        """
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE

        # Validate click coordinates
        if not (0 <= row < DIMENSION and 0 <= col < DIMENSION):
            return

        square = (row, col)

        if self.state["selected"] == square:  # Deselect if clicked twice
            self.state["selected"] = ()
            self.state["clicks"] = []
        else:
            self.state["selected"] = square
            self.state["clicks"].append(square)

        if len(self.state["clicks"]) == 2:  # Process move
            move = ChessEngine.Move(self.state["clicks"][0], self.state["clicks"][1], self.game_state.board)
            for valid_move in self.valid_moves:
                if move == valid_move:
                    self.game_state.makeMove(valid_move)
                    self.move_log.append(valid_move)
                    self.move_index += 1

                    # Start the timer after the first move
                    if not self.first_move_made:
                        self.first_move_made = True
                        self.startTimer()

                    if self.game_state.checkmate:
                        winner = "Black" if self.game_state.white_to_move else "White"
                        messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
                    elif self.game_state.stalemate:
                        messagebox.showinfo("Game Over", "Stalemate!")
                    self.state["selected"] = ()
                    self.state["clicks"] = []
                    self.valid_moves = self.game_state.getValidMoves()
                    break
            else:
                self.state["clicks"] = [square]

        self.drawBoard()
        self.highlightSquares(self.state["selected"])
        self.drawPieces(self.game_state.board)

    def startTimer(self):
        """
        Start the timer for both players.
        """
        if not self.timer_running:
            self.timer_running = True
            self.last_time_update = time.time()
            self.updateTimer()

    def updateTimer(self):
        """
        Update the timer for both players.
        """
        if self.timer_running:
            current_time = time.time()
            elapsed_time = current_time - self.last_time_update
            self.last_time_update = current_time

            if self.game_state.white_to_move:
                self.player_time -= elapsed_time
            else:
                self.opponent_time -= elapsed_time

            if self.player_time <= 0 or self.opponent_time <= 0:
                self.timer_running = False
                winner = "Black" if self.player_time <= 0 else "White"
                messagebox.showinfo("Game Over", f"Time's up! {winner} wins!")
            else:
                self.player_time_label.config(text=f"Player Time: {int(self.player_time // 60):02d}:{int(self.player_time % 60):02d}")
                self.opponent_time_label.config(text=f"Opponent Time: {int(self.opponent_time // 60):02d}:{int(self.opponent_time % 60):02d}")
                self.root.after(1000, self.updateTimer)

    def newGame(self):
        """
        Start a new game.
        """
        self.game_state = ChessEngine.GameState()
        self.valid_moves = self.game_state.getValidMoves()
        self.state = {"selected": (), "clicks": []}
        self.player_time = 600
        self.opponent_time = 600
        self.timer_running = False
        self.last_time_update = time.time()
        self.move_log = []
        self.move_index = -1
        self.first_move_made = False  # Reset first move flag
        self.drawBoard()
        self.drawPieces(self.game_state.board)
        self.player_time_label.config(text="Player Time: 10:00")
        self.opponent_time_label.config(text="Opponent Time: 10:00")

    def undoMove(self):
        """
        Undo the last move.
        """
        if self.move_index >= 0:
            self.game_state.undoMove()
            self.move_index -= 1
            self.valid_moves = self.game_state.getValidMoves()
            self.drawBoard()
            self.drawPieces(self.game_state.board)
            self.highlightSquares(self.state["selected"])

    def redoMove(self):
        """
        Redo the last undone move.
        """
        if self.move_index < len(self.move_log) - 1:
            self.move_index += 1
            self.game_state.makeMove(self.move_log[self.move_index])
            self.valid_moves = self.game_state.getValidMoves()
            self.drawBoard()
            self.drawPieces(self.game_state.board)
            self.highlightSquares(self.state["selected"])

def main():
    """
    Main function to initialize and run the chess game.
    """
    root = tk.Tk()
    ChessUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()