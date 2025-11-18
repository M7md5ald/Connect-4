"""
Connect 4 with Bitboard (42-bit integer) representation

Board layout (positions 0-41):
  0  1  2  3  4  5  6
  7  8  9 10 11 12 13
 14 15 16 17 18 19 20
 21 22 23 24 25 26 27
 28 29 30 31 32 33 34
 35 36 37 38 39 40 41

Each player has their own bitboard:
- bit = 1 means piece at that position
- bit = 0 means no piece at that position
"""

import math
import random

empty = 0
player = 1
AI = 2

rows = 6
cols = 7
WINDOW_LENGTH = 4

# Expectiminimax probabilities
PROB_CHOSEN = 0.6
PROB_NEIGHBOR = 0.2
PROB_EDGE_NEIGHBOR = 0.4


class Board:
    """Bitboard representation using two 42-bit integers"""
    
    def __init__(self):
        # Each bitboard represents positions for one player
        self.player_board = 0  # Bitboard for human player
        self.ai_board = 0      # Bitboard for AI
        
        self.column_heights = [0] * cols
        self.move_history = []
    
    def _pos(self, row, col):
        """Convert (row, col) to bit position (0-41)"""
        return row * cols + col
    
    def _set_bit(self, bitboard, row, col):
        """Set bit at (row, col) to 1"""
        return bitboard | (1 << self._pos(row, col))
    
    def _clear_bit(self, bitboard, row, col):
        """Set bit at (row, col) to 0"""
        return bitboard & ~(1 << self._pos(row, col))
    
    def _get_bit(self, bitboard, row, col):
        """Get bit value at (row, col)"""
        return (bitboard >> self._pos(row, col)) & 1
    
    def drop_piece(self, col, piece):
        """Drop a piece in the specified column"""
        row = self.column_heights[col]
        
        if piece == player:
            self.player_board = self._set_bit(self.player_board, row, col)
        elif piece == AI:
            self.ai_board = self._set_bit(self.ai_board, row, col)
        
        self.column_heights[col] += 1
        self.move_history.append((col, piece))
    
    def undo_move(self):
        """Undo the last move"""
        if not self.move_history:
            return
        
        col, piece = self.move_history.pop()
        self.column_heights[col] -= 1
        row = self.column_heights[col]
        
        if piece == player:
            self.player_board = self._clear_bit(self.player_board, row, col)
        elif piece == AI:
            self.ai_board = self._clear_bit(self.ai_board, row, col)
    
    def is_valid_location(self, col):
        """Check if column has space"""
        return self.column_heights[col] < rows
    
    def get_valid_moves(self):
        """Get list of valid column moves"""
        return [col for col in range(cols) if self.is_valid_location(col)]
    
    def is_board_full(self):
        """Check if board is completely full"""
        return len(self.move_history) == rows * cols
    
    def is_full(self):
        """Check if board is full"""
        return self.is_board_full()
    
    def get_piece(self, row, col):
        """Get piece at position (row, col)"""
        if self._get_bit(self.player_board, row, col):
            return player
        elif self._get_bit(self.ai_board, row, col):
            return AI
        return empty
    
    def copy(self):
        """Create a copy of the board"""
        new_board = Board()
        new_board.player_board = self.player_board
        new_board.ai_board = self.ai_board
        new_board.column_heights = self.column_heights[:]
        new_board.move_history = self.move_history[:]
        return new_board
    
    # For compatibility with GUI that uses board.board[row][col]
    @property
    def board(self):
        """Convert bitboards to 2D array for display"""
        grid = [[empty for _ in range(cols)] for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                grid[row][col] = self.get_piece(row, col)
        return grid


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


# ===================== TREE VISUALIZATION HELPER =====================

class TreeNode:
    """Represents a node in the minimax tree"""
    def __init__(self, node_type, depth, col=None, score=None, alpha=None, beta=None, 
                 pruned=False, probability=None, cached=False):
        self.node_type = node_type
        self.depth = depth
        self.col = col
        self.score = score
        self.alpha = alpha
        self.beta = beta
        self.pruned = pruned
        self.probability = probability
        self.cached = cached  # Mark if retrieved from transposition table
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)


def print_tree(node, prefix="", is_last=True, file=None):
    """Print the tree in a readable format"""
    connector = "└── " if is_last else "├── "
    
    label = f"{node.node_type}"
    
    if node.col is not None:
        label += f" [Col {node.col}]"
    
    if node.probability is not None:
        label += f" (p={node.probability:.2f})"
    
    if node.score is not None:
        label += f" Score: {node.score:.2f}" if isinstance(node.score, float) else f" Score: {node.score}"
    
    if node.alpha is not None or node.beta is not None:
        label += f" [α={node.alpha:.1f if node.alpha != float('-inf') and node.alpha != float('inf') else node.alpha}, β={node.beta:.1f if node.beta != float('-inf') and node.beta != float('inf') else node.beta}]"
    
    if node.cached:
        label += " 💾 CACHED"
    
    if node.pruned:
        label += " ✂️ PRUNED"
    
    print(prefix + connector + label, file=file)
    
    if node.children:
        extension = "    " if is_last else "│   "
        for i, child in enumerate(node.children):
            print_tree(child, prefix + extension, i == len(node.children) - 1, file)


# ===================== MINIMAX WITH TRANSPOSITION TABLE =====================

def minimax_with_tree(board, depth, is_maximizing, utils, indent_level=0, col_played=None):
    """Minimax algorithm with tree visualization and transposition table"""
    indent = "  " * indent_level
    
    if indent_level == 0:
        print("\n" + "="*60)
        print("MINIMAX TREE (With Transposition Table)")
        print("="*60)
        utils.transposition_table.clear()  # Clear cache for new search
    
    # Compute hash for transposition table
    board_hash = utils.compute_hash(board)
    
    # Check transposition table
    if board_hash in utils.transposition_table:
        cached_data = utils.transposition_table[board_hash]
        cached_depth, cached_score, cached_col = cached_data
        if cached_depth >= depth:
            player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
            print(f"\n{indent}┌─ Level {indent_level} | {player_type} | Col: {col_played if col_played is not None else 'ROOT'}")
            print(f"{indent}└─ 💾 CACHED (depth={cached_depth}): Score = {cached_score:.2f}")
            return cached_score, cached_col, 0
    
    player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
    print(f"\n{indent}┌─ Level {indent_level} | {player_type} | Col: {col_played if col_played is not None else 'ROOT'}")
    
    valid_moves = board.get_valid_moves()
    
    if depth == 0 or not valid_moves:
        score = utils.evaluate_board(board)
        print(f"{indent}└─ LEAF: Score = {score:.2f}")
        # Store in transposition table
        utils.transposition_table[board_hash] = (depth, score, None)
        return score, None, 1
    
    nodes_explored = 1
    
    if is_maximizing:
        max_eval = float('-inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            board.drop_piece(col, AI)
            eval_score, _, child_nodes = minimax_with_tree(
                board, depth - 1, False, utils, indent_level + 1, col
            )
            board.undo_move()
            
            nodes_explored += child_nodes
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
                print(f"{indent}│  ✓ New best move: Col {col} (score: {max_eval:.2f})")
        
        print(f"{indent}└─ MAX chooses: Col {best_col} | Score: {max_eval:.2f}")
        # Store in transposition table
        utils.transposition_table[board_hash] = (depth, max_eval, best_col)
        return max_eval, best_col, nodes_explored
    
    else:
        min_eval = float('inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            board.drop_piece(col, player)
            eval_score, _, child_nodes = minimax_with_tree(
                board, depth - 1, True, utils, indent_level + 1, col
            )
            board.undo_move()
            
            nodes_explored += child_nodes
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
                print(f"{indent}│  ✓ New best move: Col {col} (score: {min_eval:.2f})")
        
        print(f"{indent}└─ MIN chooses: Col {best_col} | Score: {min_eval:.2f}")
        # Store in transposition table
        utils.transposition_table[board_hash] = (depth, min_eval, best_col)
        return min_eval, best_col, nodes_explored


# ===================== ALPHA-BETA WITH TRANSPOSITION TABLE =====================

def alpha_beta_with_tree(board, depth, alpha, beta, is_maximizing, utils, indent_level=0, col_played=None):
    """Alpha-Beta Pruning with tree visualization and transposition table"""
    indent = "  " * indent_level
    
    if indent_level == 0:
        print("\n" + "="*60)
        print("ALPHA-BETA PRUNING (With Transposition Table)")
        print("="*60)
        utils.transposition_table.clear()
    
    # Compute hash
    board_hash = utils.compute_hash(board)
    
    # Check transposition table
    if board_hash in utils.transposition_table:
        cached_data = utils.transposition_table[board_hash]
        cached_depth, cached_score, cached_col = cached_data
        if cached_depth >= depth:
            player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
            print(f"\n{indent}┌─ Level {indent_level} | {player_type} | Col: {col_played if col_played is not None else 'ROOT'}")
            print(f"{indent}│  α={alpha:.2f}, β={beta:.2f}")
            print(f"{indent}└─ 💾 CACHED (depth={cached_depth}): Score = {cached_score:.2f}")
            return cached_score, cached_col, 0
    
    player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
    print(f"\n{indent}┌─ Level {indent_level} | {player_type} | Col: {col_played if col_played is not None else 'ROOT'}")
    print(f"{indent}│  α={alpha:.2f}, β={beta:.2f}")
    
    valid_moves = board.get_valid_moves()
    
    if depth == 0 or not valid_moves:
        score = utils.evaluate_board(board)
        print(f"{indent}└─ LEAF: Score = {score:.2f}")
        utils.transposition_table[board_hash] = (depth, score, None)
        return score, None, 1
    
    nodes_explored = 1
    
    if is_maximizing:
        max_eval = float('-inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            board.drop_piece(col, AI)
            eval_score, _, child_nodes = alpha_beta_with_tree(
                board, depth - 1, alpha, beta, False, utils, indent_level + 1, col
            )
            board.undo_move()
            
            nodes_explored += child_nodes
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
            
            alpha = max(alpha, eval_score)
            
            if beta <= alpha:
                print(f"{indent}│  ✂️ PRUNED! (β={beta:.2f} ≤ α={alpha:.2f})")
                print(f"{indent}│  Skipping remaining {len(valid_moves) - i - 1} branches")
                break
        
        print(f"{indent}└─ MAX chooses: Col {best_col} | Score: {max_eval:.2f}")
        utils.transposition_table[board_hash] = (depth, max_eval, best_col)
        return max_eval, best_col, nodes_explored
    
    else:
        min_eval = float('inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            board.drop_piece(col, player)
            eval_score, _, child_nodes = alpha_beta_with_tree(
                board, depth - 1, alpha, beta, True, utils, indent_level + 1, col
            )
            board.undo_move()
            
            nodes_explored += child_nodes
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
            
            beta = min(beta, eval_score)
            
            if beta <= alpha:
                print(f"{indent}│  ✂️ PRUNED! (β={beta:.2f} ≤ α={alpha:.2f})")
                print(f"{indent}│  Skipping remaining {len(valid_moves) - i - 1} branches")
                break
        
        print(f"{indent}└─ MIN chooses: Col {best_col} | Score: {min_eval:.2f}")
        utils.transposition_table[board_hash] = (depth, min_eval, best_col)
        return min_eval, best_col, nodes_explored


# ===================== EXPECTIMINIMAX =====================

def expectiminimax(board, depth, is_ai_turn, utils, root_call=True):
    """Expectiminimax with tree visualization"""
    if root_call:
        print("\n" + "="*70)
        print("EXPECTIMINIMAX TREE")
        print("="*70)
    
    score, col, tree = _expectiminimax_recursive(board, depth, is_ai_turn, utils, 0)
    
    if root_call:
        print_tree(tree)
    
    return score, col


def _expectiminimax_recursive(board, depth, is_ai_turn, utils, current_depth):
    """Internal recursive expectiminimax"""
    if depth == 0 or board.is_full():
        score = utils.evaluate_board(board)
        node = TreeNode("LEAF", current_depth, score=score)
        return score, None, node
    
    if is_ai_turn:
        node = TreeNode("MAX", current_depth)
        max_expected_value = -float('inf')
        best_col = None
        
        for chosen_col in board.get_valid_moves():
            expected_value, chance_node = _calculate_expected_value_tree(
                board, depth, chosen_col, utils, current_depth + 1
            )
            
            move_node = TreeNode("MAX", current_depth, col=chosen_col, score=expected_value)
            move_node.add_child(chance_node)
            node.add_child(move_node)
            
            if expected_value > max_expected_value:
                max_expected_value = expected_value
                best_col = chosen_col
        
        return max_expected_value, best_col, node
    
    else:
        node = TreeNode("MIN", current_depth)
        min_value = float('inf')
        best_col = None
        
        for col in board.get_valid_moves():
            board.drop_piece(col, player)
            new_score, _, child_node = _expectiminimax_recursive(
                board, depth - 1, True, utils, current_depth + 1
            )
            board.undo_move()
            
            move_node = TreeNode("MIN", current_depth, col=col, score=new_score)
            move_node.add_child(child_node)
            node.add_child(move_node)
            
            if new_score < min_value:
                min_value = new_score
                best_col = col
        
        return min_value, best_col, node


def _calculate_expected_value_tree(board, depth, chosen_col, utils, current_depth):
    """Calculate expected value with tree building for chance node"""
    chance_node = TreeNode("CHANCE", current_depth, col=chosen_col)
    total_expected_value = 0.0
    
    outcomes = []
    
    left_valid = (chosen_col > 0) and board.is_valid_location(chosen_col - 1)
    right_valid = (chosen_col < cols - 1) and board.is_valid_location(chosen_col + 1)
    
    if left_valid and right_valid:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((chosen_col - 1, PROB_NEIGHBOR))
        outcomes.append((chosen_col + 1, PROB_NEIGHBOR))
    elif left_valid:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((chosen_col - 1, PROB_EDGE_NEIGHBOR))
    elif right_valid:
        outcomes.append((chosen_col, PROB_CHOSEN))
        outcomes.append((chosen_col + 1, PROB_EDGE_NEIGHBOR))
    else:
        outcomes.append((chosen_col, 1.0))
    
    for landing_col, prob in outcomes:
        board.drop_piece(landing_col, AI)
        value_of_outcome, _, child_node = _expectiminimax_recursive(
            board, depth - 1, False, utils, current_depth + 1
        )
        board.undo_move()
        
        prob_node = TreeNode("CHANCE", current_depth, col=landing_col, 
                            score=value_of_outcome, probability=prob)
        prob_node.add_child(child_node)
        chance_node.add_child(prob_node)
        
        total_expected_value += prob * value_of_outcome
    
    chance_node.score = total_expected_value
    return total_expected_value, chance_node


# Backward compatibility wrappers
def minimax(board, depth, maximizing_player, utils, root_call=True):
    """Wrapper for compatibility"""
    score, col, nodes = minimax_with_tree(board, depth, maximizing_player, utils, 0, None)
    node = TreeNode("MAX" if maximizing_player else "MIN", 0, score=score)
    return score, col, node


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, utils, root_call=True):
    """Wrapper for compatibility"""
    score, col, nodes = alpha_beta_with_tree(board, depth, alpha, beta, maximizing_player, utils, 0, None)
    node = TreeNode("MAX" if maximizing_player else "MIN", 0, score=score)
    return score, col, node