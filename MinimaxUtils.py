from board import Board
import math

EMPTY = 0
PLAYER = 1
AI = 2

ROWS = 6
COLS = 7
WINDOW_LENGTH = 4

class MinimaxUtils:
    def __init__(self):
        pass

    def is_terminal(self, board, depth):
        return depth == 0 or board.is_full()

    def evaluate_board(self, board):
        """
        Return heuristic score for the board FROM AI'S PERSPECTIVE.
        Positive = Good for AI (maximizer)
        Negative = Good for Human (minimizer)
        """
        score = 0

        # Score center column higher (strategic advantage)
        center_col = COLS // 2
        center_count = sum(1 for r in range(ROWS) if board.board[r][center_col] == AI)
        score += center_count * 6

        # Score all windows
        score += self.score_position(board, AI)      # AI's opportunities (positive)
        score -= self.score_position(board, PLAYER)  # Human's opportunities (negative)
        
        return score

    def score_position(self, board, piece):
        """
        Score all possible windows of 4 pieces FOR the given piece.
        Returns POSITIVE values for that piece's advantages.
        """
        score = 0
        opp_piece = PLAYER if piece == AI else AI

        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = [board.board[r][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)

        # Vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                window = [board.board[r + i][c] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)

        # Diagonal down-right
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board.board[r + i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)

        # Diagonal down-left
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                window = [board.board[r + i][c - i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)

        return score

    def evaluate_window(self, window, piece, opp_piece):
       
        score = 0

        piece_count = window.count(piece)
        opp_count = window.count(opp_piece)
        empty_count = window.count(EMPTY)

        # Our piece's opportunities (POSITIVE)
        if piece_count == 4:
            score += 100000  # Four in a row - winning position
        elif piece_count == 3 and empty_count == 1:
            score += 100     # Three in a row with space - strong threat
        elif piece_count == 2 and empty_count == 2:
            score += 10      # Two in a row with space - developing
        elif piece_count == 1 and empty_count == 3:
            score += 1       # One piece with space - potential

        # Opponent's threats (NEGATIVE for us)
        if opp_count == 3 and empty_count == 1:
            score -= 90      # Opponent about to win - VERY BAD for us!
        elif opp_count == 2 and empty_count == 2:
            score -= 5       # Opponent developing - somewhat bad

        return score

    def check_win(self, board, piece):
        """Check if the given piece has won"""
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(board.board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                    return True
        # Vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(board.board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                    return True
        # Diagonal down-right
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(board.board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                    return True
        # Diagonal down-left
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                if all(board.board[r + i][c - i] == piece for i in range(WINDOW_LENGTH)):
                    return True
        return False


