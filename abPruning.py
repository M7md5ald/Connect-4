import math
import random

import TreeNode

empty = 0
player = 1
AI = 2

rows = 6
cols = 7
WINDOW_LENGTH = 4

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


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player, utils, root_call=True):
    """Wrapper for compatibility"""
    score, col, nodes = alpha_beta_with_tree(board, depth, alpha, beta, maximizing_player, utils, 0, None)
    node = TreeNode("MAX" if maximizing_player else "MIN", 0, score=score)
    return score, col, node