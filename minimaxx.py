from board import Board
from TreeNode import TreeNode, print_tree ,print_board_state, print_tree_node

import math

EMPTY = 0
PLAYER = 1
AI = 2

ROWS = 6
COLS = 7
WINDOW_LENGTH = 4
def minimax(board, depth, maximizing_player, utils, root_call=True):
    """Minimax with tree visualization"""
    if root_call:
        print("\n" + "="*70)
        print("MINIMAX TREE (No Pruning)")
        print("="*70)
    
    return _minimax_recursive(board, depth, maximizing_player, utils, 0)


def _minimax_recursive(board, depth, maximizing_player, utils, current_depth):
    """Internal recursive minimax with tree building"""
    
    # Create node
    node_type = "MAX" if maximizing_player else "MIN"
    
    # Terminal condition
    if utils.is_terminal(board, depth):
        score = utils.evaluate_board(board)
        node = TreeNode("LEAF", current_depth, score=score)
        if current_depth == 0:
            print_tree(node)
        return score, None, node

    valid_moves = board.get_valid_moves()
    node = TreeNode(node_type, current_depth)

    if maximizing_player:
        max_eval = -math.inf
        best_col = valid_moves[0]
        
        for col in valid_moves:
            board.drop_piece(col, AI)
            eval_score, _, child_node = _minimax_recursive(board, depth - 1, False, utils, current_depth + 1)
            board.undo_move()
            
            # Create child node for this move
            move_node = TreeNode("MAX", current_depth, col=col, score=eval_score)
            move_node.add_child(child_node)
            node.add_child(move_node)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
        
        if current_depth == 0:
            print_tree(node)
        
        return max_eval, best_col, node
    else:
        min_eval = math.inf
        best_col = valid_moves[0]
        
        for col in valid_moves:
            board.drop_piece(col, PLAYER)
            eval_score, _, child_node = _minimax_recursive(board, depth - 1, True, utils, current_depth + 1)
            board.undo_move()
            
            # Create child node for this move
            move_node = TreeNode("MIN", current_depth, col=col, score=eval_score)
            move_node.add_child(child_node)
            node.add_child(move_node)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
        
        if current_depth == 0:
            print_tree(node)
        
        return min_eval, best_col, node

def minimax_with_tree(board, depth, is_maximizing, utils, indent_level=0, col_played=None):

    indent = "  " * indent_level
    
    # Print current node
    if indent_level == 0:
        print("\n" + "="*60)
        print("MINIMAX TREE VISUALIZATION")
        print("="*60)
    
    player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
    print(f"\n{indent}┌─ Level {indent_level} | {player_type} | Col: {col_played if col_played is not None else 'ROOT'}")
    
    # Print board state
    if indent_level <= 6 :  # Only show board for first few levels to avoid clutter
        print_board_state(board, indent + "│  ")
    
    # Terminal conditions
    valid_moves = board.get_valid_moves()
    
    if depth == 0 or not valid_moves:
        score = utils.evaluate_board(board)
        print(f"{indent}└─ LEAF: Score = {score:.2f}")
        return score, None, 0
    
    nodes_explored = 1
    
    if is_maximizing:
        max_eval = float('-inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            # Make move
            temp_board = board.copy()
            temp_board.drop_piece(col, AI)
            
            # Recursive call
            eval_score, _, child_nodes = minimax_with_tree(
                temp_board, depth - 1, False, utils, indent_level + 1, col
            )
            nodes_explored += child_nodes
            
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col
                print(f"{indent}│  ✓ New best move: Col {col} (score: {max_eval:.2f})")
        
        print(f"{indent}└─ MAX chooses: Col {best_col} | Score: {max_eval:.2f}")
        return max_eval, best_col, nodes_explored
    
    else:  # Minimizing
        min_eval = float('inf')
        best_col = valid_moves[0] if valid_moves else None
        
        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")
        
        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)})")
            
            # Make move
            temp_board = board.copy()
            temp_board.drop_piece(col, PLAYER)
            
            # Recursive call
            eval_score, _, child_nodes = minimax_with_tree(
                temp_board, depth - 1, True, utils, indent_level + 1, col
            )
            nodes_explored += child_nodes
            
            print(f"{indent}│  ← Column {col} returned: {eval_score:.2f}")
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col
                print(f"{indent}│  ✓ New best move: Col {col} (score: {min_eval:.2f})")
        
        print(f"{indent}└─ MIN chooses: Col {best_col} | Score: {min_eval:.2f}")
        return min_eval, best_col, nodes_explored

