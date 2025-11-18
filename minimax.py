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
        return depth == 0 or board.is_full() #or self.check_win(board, PLAYER) or self.check_win(board, AI)

    def evaluate_board(self, board):
        """Return heuristic score for the board with blocking priority."""
        score = 0

        # Score center column higher
        center_col = COLS // 2
        center_count = sum(1 for r in range(ROWS) if board.board[r][center_col] == AI)
        score += center_count * 3 #more piority for center

        # Score all windows
        score += self.score_position(board, AI)  #calculates the score for all horizontal, vertical, and diagonal sequences.
        score -= self.score_position(board, PLAYER)  # subtract opponent potential
        return score

    def score_position(self, board, piece):
        """Score all possible windows of 4 pieces."""
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
        """Evaluate a window of 4 squares for heuristic scoring with blocking priority."""
        score = 0

        # Check for AI winning line
        if window.count(piece) == 4:
            score += 100
        # Check for AI 3 in a row
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 10
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 5

        # Check for opponent 3 in a row — **blocking has higher priority**
        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 50  # high negative to force blocking

        return score

    def check_win(self, board, piece):
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

# --------------------- Minimax Algorithm ---------------------
def minimax(board, depth, maximizing_player, utils):
    if utils.is_terminal(board, depth):
        return utils.evaluate_board(board), None

    valid_moves = board.get_valid_moves()

    if maximizing_player:
        max_eval = -math.inf
        best_col = None
        for col in valid_moves:
            board.drop_piece(col, AI)
            eval_score, _ = minimax(board, depth - 1, False, utils)
            board.undo_move()
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
        return max_eval, best_col
    else:
        min_eval = math.inf
        best_col = None
        for col in valid_moves:
            board.drop_piece(col, PLAYER)
            eval_score, _ = minimax(board, depth - 1, True, utils)
            board.undo_move()
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
        return min_eval, best_col

# --------------------- (Alpha-Beta Pruning Minimax Algorithm) ---------------------

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, utils):
    if utils.is_terminal(board, depth):
        return utils.evaluate_board(board), None

    valid_moves = board.get_valid_moves()

    if maximizing_player:
        max_eval = -math.inf
        best_col = None
        for col in valid_moves:
            board.drop_piece(col, AI)
            eval_score, _ = minimax_alpha_beta(board, depth - 1, alpha, beta, False, utils)
            board.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col

            # Alpha-Beta update for maximizing player
            alpha = max(alpha, eval_score)
            if alpha >= beta:   # prune
                break

        return max_eval, best_col

    else:
        min_eval = math.inf
        best_col = None
        for col in valid_moves:
            board.drop_piece(col, PLAYER)
            eval_score, _ = minimax_alpha_beta(board, depth - 1, alpha, beta, True, utils)
            board.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col

            # Alpha-Beta update for minimizing player
            beta = min(beta, eval_score)
            if beta <= alpha:   # prune
                break

        return min_eval, best_col