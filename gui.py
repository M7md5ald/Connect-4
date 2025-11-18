import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from board import Board, empty, player, AI, rows, cols
from board import MinimaxUtils, minimax, minimax_alpha_beta, expectiminimax , minimax_with_tree, alpha_beta_with_tree
import time
import sys
from io import StringIO


class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - AI Assignment")
        self.root.configure(bg='#f0f0f0')

        # Game state
        self.board = Board()
        self.utils = MinimaxUtils()
        self.game_over = False
        self.current_player = player  # Human starts
        self.selected_algorithm = tk.StringVar(value="minimax")
        self.game_started = False
        self.depth = tk.IntVar(value=4)

        # Scores
        self.player_fours = 0
        self.ai_fours = 0

        # Colors
        self.BLUE = '#0077b6'
        self.RED = '#e63946'
        self.YELLOW = '#ffd60a'
        self.EMPTY_COLOR = '#023e8a'

        # Cell size
        self.cell_size = 70

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Top frame for board and menu
        top_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Board frame (left side)
        board_frame = tk.Frame(top_frame, bg='#f0f0f0', relief=tk.RAISED, borderwidth=2)
        board_frame.pack(side=tk.LEFT, padx=(0, 10))

        # Canvas for the board
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size
        self.canvas = tk.Canvas(
            board_frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.BLUE,
            highlightthickness=2,
            highlightbackground='black'
        )
        self.canvas.pack(padx=5, pady=5)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_mouse_move)

        # Draw initial board
        self.draw_board()

        # Menu frame (right side)
        menu_frame = tk.Frame(top_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 0))

        # Menu title
        title_label = tk.Label(
            menu_frame,
            text="AI Settings",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#023e8a'
        )
        title_label.pack(pady=(10, 20))

        # Algorithm selection
        algo_label = tk.Label(
            menu_frame,
            text="Select Algorithm:",
            font=('Arial', 11, 'bold'),
            bg='white'
        )
        algo_label.pack(anchor=tk.W, padx=20, pady=(0, 5))

        algorithms = [
            ("Minimax (No Pruning)", "minimax"),
            ("Alpha-Beta Pruning", "alpha_beta"),
            ("Expectiminimax", "expectiminimax")
        ]

        for text, value in algorithms:
            rb = tk.Radiobutton(
                menu_frame,
                text=text,
                variable=self.selected_algorithm,
                value=value,
                font=('Arial', 10),
                bg='white',
                activebackground='white',
                command=self.on_algorithm_change
            )
            rb.pack(anchor=tk.W, padx=30, pady=2)

        # Depth selection
        depth_frame = tk.Frame(menu_frame, bg='white')
        depth_frame.pack(pady=(20, 10), padx=20, fill=tk.X)

        depth_label = tk.Label(
            depth_frame,
            text="Search Depth (K):",
            font=('Arial', 11, 'bold'),
            bg='white'
        )
        depth_label.pack(side=tk.LEFT)

        depth_spinbox = tk.Spinbox(
            depth_frame,
            from_=1,
            to=8,
            textvariable=self.depth,
            width=5,
            font=('Arial', 10),
            command=self.on_depth_change
        )
        depth_spinbox.pack(side=tk.LEFT, padx=10)

        # Buttons
        button_frame = tk.Frame(menu_frame, bg='white')
        button_frame.pack(pady=20, padx=20, fill=tk.X)

        self.start_button = tk.Button(
            button_frame,
            text="Start Game",
            command=self.start_game,
            bg='#2a9d8f',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            relief=tk.RAISED,
            cursor='hand2'
        )
        self.start_button.pack(pady=5)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset Game",
            command=self.reset_game,
            bg='#e76f51',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            relief=tk.RAISED,
            cursor='hand2'
        )
        self.reset_button.pack(pady=5)

        # Status display
        status_frame = tk.Frame(menu_frame, bg='white')
        status_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            status_frame,
            text="Status:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W)

        self.status_label = tk.Label(
            status_frame,
            text="Not Started",
            font=('Arial', 10),
            bg='white',
            fg='red'
        )
        self.status_label.pack(anchor=tk.W, padx=10)

        tk.Label(
            status_frame,
            text="Current Turn:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, pady=(10, 0))

        self.turn_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 10),
            bg='white'
        )
        self.turn_label.pack(anchor=tk.W, padx=10)

        # Score display
        score_frame = tk.Frame(menu_frame, bg='white')
        score_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            score_frame,
            text="Connect-4 Count:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor=tk.W)

        self.score_label = tk.Label(
            score_frame,
            text="Human: 0 | AI: 0",
            font=('Arial', 10),
            bg='white',
            fg='#023e8a'
        )
        self.score_label.pack(anchor=tk.W, padx=10)

        # Terminal (bottom)
        terminal_frame = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, borderwidth=2)
        terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(10, 0))

        terminal_label = tk.Label(
            terminal_frame,
            text="Console Output (Tree Visualization):",
            font=('Arial', 11, 'bold'),
            bg='white',
            anchor=tk.W
        )
        terminal_label.pack(fill=tk.X, padx=5, pady=5)

        self.terminal = scrolledtext.ScrolledText(
            terminal_frame,
            height=50,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Courier', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Initial messages
        self.add_terminal_message("Welcome to Connect 4!")
        self.add_terminal_message("Select an algorithm and depth to start.")
        self.add_terminal_message("Tree will be displayed in console for each AI move.")

    def draw_board(self):
        """Draw the Connect 4 board with pieces"""
        self.canvas.delete("all")

        # Draw grid and pieces
        for row in range(rows):
            for col in range(cols):
                # FLIP the visual representation: row 0 at bottom
                visual_row = rows - 1 - row

                x1 = col * self.cell_size
                y1 = visual_row * self.cell_size
                x_center = x1 + self.cell_size // 2
                y_center = y1 + self.cell_size // 2
                radius = self.cell_size // 2 - 5

                # Get piece from board
                piece = self.board.board[row][col]
                if piece == player:
                    color = self.RED
                elif piece == AI:
                    color = self.YELLOW
                else:
                    color = self.EMPTY_COLOR

                self.canvas.create_oval(
                    x_center - radius, y_center - radius,
                    x_center + radius, y_center + radius,
                    fill=color,
                    outline='black',
                    width=2
                )

    def on_canvas_click(self, event):
        """Handle click on the board"""
        if not self.game_started or self.game_over or self.current_player != player:
            return

        col = event.x // self.cell_size
        if 0 <= col < cols and self.board.is_valid_location(col):
            self.make_move(col)

    def on_mouse_move(self, event):
        """Show hover effect on valid columns"""
        if not self.game_started or self.game_over or self.current_player != player:
            self.canvas.config(cursor="")
            return

        col = event.x // self.cell_size
        if 0 <= col < cols and self.board.is_valid_location(col):
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")

    def count_fours(self, piece):
        """Count the number of connect-4s for a given piece"""
        count = 0

        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                if all(self.board.board[r][c + i] == piece for i in range(4)):
                    count += 1

        # Vertical
        for r in range(rows - 3):
            for c in range(cols):
                if all(self.board.board[r + i][c] == piece for i in range(4)):
                    count += 1

        # Diagonal down-right
        for r in range(rows - 3):
            for c in range(cols - 3):
                if all(self.board.board[r + i][c + i] == piece for i in range(4)):
                    count += 1

        # Diagonal down-left
        for r in range(rows - 3):
            for c in range(3, cols):
                if all(self.board.board[r + i][c - i] == piece for i in range(4)):
                    count += 1

        return count

    def update_scores(self):
        """Update the connect-4 count for both players"""
        self.player_fours = self.count_fours(player)
        self.ai_fours = self.count_fours(AI)
        self.score_label.config(text=f"Human: {self.player_fours} | AI: {self.ai_fours}")

    def check_game_over(self):
        """Check if game is over and determine winner"""
        if not self.board.get_valid_moves():
            self.game_over = True
            self.update_scores()

            if self.player_fours > self.ai_fours:
                winner = "Human Wins!"
                color = self.RED
            elif self.ai_fours > self.player_fours:
                winner = "AI Wins!"
                color = self.YELLOW
            else:
                winner = "It's a Tie!"
                color = '#023e8a'

            self.status_label.config(text=winner, fg=color)
            self.turn_label.config(text="Game Over")

            self.add_terminal_message("=" * 50)
            self.add_terminal_message("GAME OVER!")
            self.add_terminal_message(f"Final Score - Human: {self.player_fours} | AI: {self.ai_fours}")
            self.add_terminal_message(f"Result: {winner}")
            self.add_terminal_message("=" * 50)

            messagebox.showinfo("Game Over",
                                f"{winner}\n\nFinal Score:\nHuman: {self.player_fours} Connect-4s\nAI: {self.ai_fours} Connect-4s")

            return True
        return False

    def make_move(self, col):
        """Make a move on the board"""
        self.board.drop_piece(col, self.current_player)
        self.draw_board()

        player_name = "Human (Red)" if self.current_player == player else "AI (Yellow)"
        self.add_terminal_message(f"{player_name} moved in column {col}")

        self.update_scores()

        if self.check_game_over():
            return

        # Switch player
        self.current_player = AI if self.current_player == player else player
        self.update_turn_label()

        # Trigger AI move
        if self.current_player == AI and not self.game_over:
            self.root.after(500, self.ai_move)

    def ai_move(self):
        """Execute AI move with tree visualization"""
        valid_moves = self.board.get_valid_moves()
        if not valid_moves:
            self.add_terminal_message("ERROR: No valid moves available!")
            self.check_game_over()
            return

        self.add_terminal_message("\n" + "🤖 AI is thinking...")
        self.root.update()

        algo = self.selected_algorithm.get()
        depth = self.depth.get()

        if depth > 6:
            self.add_terminal_message(f"⚠️ Depth {depth} may take a long time...")
            self.root.update()

        start_time = time.time()

        try:
            # Capture tree output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
          
            if algo == "minimax":
                score, col, nodes = minimax_with_tree(self.board, depth, True, self.utils)
                self.add_terminal_message(f"Nodes explored: {nodes}")
            elif algo == "alpha_beta":
                score, col, nodes = alpha_beta_with_tree(self.board, depth, float('-inf'), float('inf'), True, self.utils)
                self.add_terminal_message(f"Nodes explored: {nodes}")
            else:  # expectiminimax
                score, col = expectiminimax(self.board, depth, True, self.utils)
            
            # Get captured output
            tree_output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Display tree in terminal
            self.add_terminal_message(tree_output)
            
            end_time = time.time()
            elapsed = end_time - start_time

            if col is not None and col in valid_moves:
                self.add_terminal_message(f"\n✅ AI chose column {col} (score: {score:.2f})")
                self.add_terminal_message(f"⏱️ Time taken: {elapsed:.4f} seconds")
                self.add_terminal_message("")
                self.make_move(col)
            else:
                self.add_terminal_message(f"ERROR: AI returned invalid column: {col}")
                import random
                fallback_col = random.choice(valid_moves)
                self.add_terminal_message(f"Making random fallback move: column {fallback_col}")
                self.make_move(fallback_col)

        except RecursionError:
            sys.stdout = old_stdout
            self.add_terminal_message("ERROR: Recursion limit reached! Reduce depth.")
        except MemoryError:
            sys.stdout = old_stdout
            self.add_terminal_message("ERROR: Out of memory! Reduce depth.")
        except Exception as e:
            sys.stdout = old_stdout
            self.add_terminal_message(f"ERROR: {str(e)}")
            import traceback
            self.add_terminal_message(traceback.format_exc())

    def start_game(self):
        """Start the game"""
        if not self.game_started:
            self.game_started = True
            self.status_label.config(text="Game Active", fg='green')
            self.update_turn_label()
            algo_name = self.selected_algorithm.get()
            self.add_terminal_message("=" * 50)
            self.add_terminal_message(f"🎮 Game started!")
            self.add_terminal_message(f"Algorithm: {algo_name}")
            self.add_terminal_message(f"Search Depth: {self.depth.get()}")
            self.add_terminal_message("=" * 50)

    def reset_game(self):
        """Reset the game"""
        self.board = Board()
        self.game_over = False
        self.current_player = player
        self.game_started = False
        self.player_fours = 0
        self.ai_fours = 0
        self.status_label.config(text="Not Started", fg='red')
        self.turn_label.config(text="")
        self.score_label.config(text="Human: 0 | AI: 0")
        self.draw_board()
        self.add_terminal_message("=" * 50)
        self.add_terminal_message("🔄 Game reset!")
        self.add_terminal_message("=" * 50)

    def update_turn_label(self):
        """Update the turn label"""
        if self.game_started and not self.game_over:
            if self.current_player == player:
                self.turn_label.config(text="Human (Red)", fg=self.RED)
            else:
                self.turn_label.config(text="AI (Yellow)", fg='#997a00')
        else:
            self.turn_label.config(text="")

    def on_algorithm_change(self):
        """Handle algorithm selection change"""
        algo_names = {
            "minimax": "Minimax (No Pruning)",
            "alpha_beta": "Alpha-Beta Pruning",
            "expectiminimax": "Expectiminimax"
        }
        algo = self.selected_algorithm.get()
        self.add_terminal_message(f"Algorithm selected: {algo_names[algo]}")

    def on_depth_change(self):
        """Handle depth change"""
        self.add_terminal_message(f"Depth changed to: {self.depth.get()}")

    def add_terminal_message(self, message):
        """Add a message to the terminal"""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, message + "\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()