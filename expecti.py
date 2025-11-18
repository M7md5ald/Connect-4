from board import Board
from TreeNode import TreeNode, print_tree ,print_board_state, print_tree_node
import math

EMPTY = 0
PLAYER = 1
AI = 2

ROWS = 6
COLS = 7
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
    """Internal recursive expectiminimax with tree building"""
    
    # Terminal condition
    if depth == 0 or board.is_full():
        score = utils.evaluate_board(board)
        node = TreeNode("LEAF", current_depth, score=score)
        return score, None, node

    # MAX Node (AI)
    if is_ai_turn:
        node = TreeNode("MAX", current_depth)
        max_expected_value = -float('inf')
        best_col = None
        
        for chosen_col in board.get_valid_moves():
            # Calculate expected value through chance node
            expected_value, chance_node = _calculate_expected_value_tree(
                board, depth, chosen_col, utils, current_depth + 1
            )
            
            # Create move node
            move_node = TreeNode("MAX", current_depth, col=chosen_col, score=expected_value)
            move_node.add_child(chance_node)
            node.add_child(move_node)
            
            if expected_value > max_expected_value:
                max_expected_value = expected_value
                best_col = chosen_col
        
        return max_expected_value, best_col, node
    
    # MIN Node (Human)
    else:
        node = TreeNode("MIN", current_depth)
        min_value = float('inf')
        best_col = None
        
        for col in board.get_valid_moves():
            board.drop_piece(col, PLAYER)
            new_score, _, child_node = _expectiminimax_recursive(
                board, depth - 1, True, utils, current_depth + 1
            )
            board.undo_move()
            
            # Create move node
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
    right_valid = (chosen_col < COLS - 1) and board.is_valid_location(chosen_col + 1)

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

    # Calculate weighted average
    for landing_col, prob in outcomes:
        board.drop_piece(landing_col, AI)
        value_of_outcome, _, child_node = _expectiminimax_recursive(
            board, depth - 1, False, utils, current_depth + 1
        )
        board.undo_move()
        
        # Create probability node
        prob_node = TreeNode("CHANCE", current_depth, col=landing_col, 
                            score=value_of_outcome, probability=prob)
        prob_node.add_child(child_node)
        chance_node.add_child(prob_node)
        
        total_expected_value += prob * value_of_outcome
    
    chance_node.score = total_expected_value
    return total_expected_value, chance_node
def expecti_with_tree(board, depth, is_ai_turn, utils, indent_level=0, col_played=None, prob=1.0):
    indent = "  " * indent_level

    # Root display
    if indent_level == 0:
        print("\n" + "="*70)
        print("EXPECTIMINIMAX TREE VISUALIZATION")
        print("="*70)

    # Node type
    if is_ai_turn:
        node_type = "MAX (AI)"
    else:
        node_type = "MIN (Human)"

    # Print node header
    print(f"\n{indent}┌─ Level {indent_level} | {node_type} | Col: {col_played if col_played is not None else 'ROOT'}")
    print(f"{indent}│  Probability = {prob:.2f}")

    # Print the board (like alpha-beta)
    print_board_state(board, indent + "│  ")

    # Terminal state
    if depth == 0 or board.is_full():
        score = utils.evaluate_board(board)
        print(f"{indent}└─ LEAF: Score = {score:.2f}")
        return score, None

    valid_moves = board.get_valid_moves()

    # ----------------------------
    # MAX NODE (AI)
    # ----------------------------
    if is_ai_turn:
        best_val = -float("inf")
        best_col = None

        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")

        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Trying column {col} ({i+1}/{len(valid_moves)}) → CHANCE NODE")

            expected_value = evaluate_chance_node_with_tree(
                board, depth, col, utils, indent_level + 1
            )

            print(f"{indent}│  ← Expected value from CHANCE({col}) = {expected_value:.2f}")

            if expected_value > best_val:
                best_val = expected_value
                best_col = col

        print(f"{indent}└─ MAX chooses col {best_col} | Score: {best_val:.2f}")
        return best_val, best_col

    # ----------------------------
    # MIN NODE (Human)
    # ----------------------------
    else:
        best_val = float("inf")
        best_col = None

        print(f"{indent}│  Exploring {len(valid_moves)} moves: {valid_moves}")

        for i, col in enumerate(valid_moves):
            print(f"{indent}│")
            print(f"{indent}├─► Human tries column {col} ({i+1}/{len(valid_moves)})")

            board.drop_piece(col, PLAYER)

            val, _ = expecti_with_tree(board, depth - 1, True, utils, indent_level + 1, col)

            board.undo_move()

            print(f"{indent}│  ← MIN returned value {val:.2f}")

            if val < best_val:
                best_val = val
                best_col = col

        print(f"{indent}└─ MIN chooses col {best_col} | Score: {best_val:.2f}")
        return best_val, best_col


# -----------------------------------------------------
# CHANCE NODE HANDLER
# -----------------------------------------------------
def evaluate_chance_node_with_tree(board, depth, chosen_col, utils, indent_level):
    indent = "  " * indent_level

    print(f"{indent}┌─ CHANCE Node at Level {indent_level} | For chosen col = {chosen_col}")

    outcomes = []
    total = 0

    # Check neighbors
    left_valid = chosen_col > 0 and board.is_valid_location(chosen_col - 1)
    right_valid = chosen_col < COLS - 1 and board.is_valid_location(chosen_col + 1)

    if left_valid and right_valid:
        outcomes = [
            (chosen_col, PROB_CHOSEN),
            (chosen_col - 1, PROB_NEIGHBOR),
            (chosen_col + 1, PROB_NEIGHBOR),
        ]
    elif left_valid:
        outcomes = [
            (chosen_col, PROB_CHOSEN),
            (chosen_col - 1, PROB_EDGE_NEIGHBOR),
        ]
    elif right_valid:
        outcomes = [
            (chosen_col, PROB_CHOSEN),
            (chosen_col + 1, PROB_EDGE_NEIGHBOR),
        ]
    else:
        outcomes = [(chosen_col, 1.0)]

    # Display available outcomes
    for c, p in outcomes:
        print(f"{indent}│  Outcome: drop at {c} with prob={p:.2f}")

    print()

    expected_value = 0

    # Evaluate all chance outcomes
    for landing_col, prob in outcomes:
        print(f"{indent}├─► Chance outcome: drop at {landing_col} | prob={prob:.2f}")

        board.drop_piece(landing_col, AI)

        val, _ = expecti_with_tree(
            board, depth - 1, False, utils, indent_level + 1, landing_col, prob
        )

        board.undo_move()

        print(f"{indent}│  ← Chance returned {val:.2f} (weighted {prob * val:.2f})")

        expected_value += prob * val

    print(f"{indent}└─ CHANCE aggregated value = {expected_value:.2f}")

    return expected_value
