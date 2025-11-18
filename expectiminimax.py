
from TreeNode import *


empty = 0
player = 1
AI = 2

rows = 6
cols = 7

WINDOW_LENGTH = 4
PROB_CHOSEN = 0.6
PROB_NEIGHBOR = 0.2
PROB_EDGE_NEIGHBOR = 0.4

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


