import random
empty = 0
player = 1
AI = 2

rows = 6
cols = 7
WINDOW_LENGTH = 4
class MinimaxUtils:
    def __init__(self):
        # Initialize Zobrist hashing table
        self.zobrist_table = self._init_zobrist()
        self.transposition_table = {}
    
    def _init_zobrist(self):
        """Initialize random values for Zobrist hashing"""
        random.seed(42)  # Fixed seed for reproducibility
        # 42 positions × 2 players (PLAYER and AI)
        return [[random.getrandbits(64) for _ in range(2)] for _ in range(42)]
    
    def compute_hash(self, board):
        """Compute Zobrist hash for current board state"""
        h = 0
        for row in range(rows):
            for col in range(cols):
                pos = row * cols + col
                piece = board.get_piece(row, col)
                if piece == player:
                    h ^= self.zobrist_table[pos][0]
                elif piece == AI:
                    h ^= self.zobrist_table[pos][1]
        return h
    
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
        center_col = cols // 2
        center_count = sum(1 for r in range(rows) if board.get_piece(r, center_col) == AI)
        score += center_count * 6
        
        # Score all windows
        score += self.score_position(board, AI)      # AI's opportunities (positive)
        score -= self.score_position(board, player)  # Human's opportunities (negative)
        
        return score
    
    def score_position(self, board, piece):
        """
        Score all possible windows of 4 pieces FOR the given piece.
        Returns POSITIVE values for that piece's advantages.
        """
        score = 0
        opp_piece = player if piece == AI else AI
        
        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                window = [board.get_piece(r, c + i) for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)
        
        # Vertical
        for r in range(rows - 3):
            for c in range(cols):
                window = [board.get_piece(r + i, c) for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)
        
        # Diagonal down-right
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [board.get_piece(r + i, c + i) for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)
        
        # Diagonal down-left
        for r in range(rows - 3):
            for c in range(3, cols):
                window = [board.get_piece(r + i, c - i) for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece, opp_piece)
        
        return score
    
    def evaluate_window(self, window, piece, opp_piece):
        """Evaluate a window of 4 squares FROM THE PERSPECTIVE of 'piece'"""
        score = 0
        
        piece_count = window.count(piece)
        opp_count = window.count(opp_piece)
        empty_count = window.count(empty)
        
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
        """Check if the given piece has won using bitboard operations"""
        # Get the bitboard for this piece
        if piece == player:
            bitboard = board.player_board
        elif piece == AI:
            bitboard = board.ai_board
        else:
            return False
        
        # Horizontal check: shift by 1
        if bitboard & (bitboard >> 1) & (bitboard >> 2) & (bitboard >> 3):
            # Verify it's not wrapping across rows
            for r in range(rows):
                for c in range(cols - 3):
                    if all(board.get_piece(r, c + i) == piece for i in range(4)):
                        return True
        
        # Vertical check: shift by 7 (COLS)
        if bitboard & (bitboard >> cols) & (bitboard >> (2*cols)) & (bitboard >> (3*cols)):
            return True
        
        # Diagonal down-right: shift by 8 (COLS + 1)
        if bitboard & (bitboard >> (cols+1)) & (bitboard >> (2*(cols+1))) & (bitboard >> (3*(cols+1))):
            # Verify valid diagonal
            for r in range(rows - 3):
                for c in range(cols - 3):
                    if all(board.get_piece(r + i, c + i) == piece for i in range(4)):
                        return True
        
        # Diagonal down-left: shift by 6 (COLS - 1)
        if bitboard & (bitboard >> (cols-1)) & (bitboard >> (2*(cols-1))) & (bitboard >> (3*(cols-1))):
            # Verify valid diagonal
            for r in range(rows - 3):
                for c in range(3, cols):
                    if all(board.get_piece(r + i, c - i) == piece for i in range(4)):
                        return True
        
        return False
