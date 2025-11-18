from TreeNode import TreeNode
from board import Board

empty = 0
player = 1
AI = 2

rows = 6
cols = 7
WINDOW_LENGTH = 4
PROB_CHOSEN = 0.6
PROB_NEIGHBOR = 0.2
PROB_EDGE_NEIGHBOR = 0.4


def expectiminimax(board: Board, depth, is_ai_turn, utils):
    """Run expectiminimax and print the tree with boards in console"""
    score, best_col, tree = _expectiminimax_recursive(board, depth, is_ai_turn, utils, 0)
    
    print("\n" + "="*70)
    print("EXPECTIMINIMAX TREE WITH BOARDS")
    print("="*70)
    print_tree(tree, board)
    
    return score, best_col


def _expectiminimax_recursive(board: Board, depth, is_ai_turn, utils, current_depth):
    """Recursive expectiminimax"""
    if depth == 0 or board.is_full():
        score = utils.evaluate_board(board)
        node = TreeNode("LEAF", current_depth, score=score)
        return score, None, node

    valid_moves = board.get_valid_moves()
    if not valid_moves:
        score = utils.evaluate_board(board)
        node = TreeNode("LEAF", current_depth, score=score)
        return score, None, node

    if is_ai_turn:
        max_score = -float('inf')
        best_col = None
        node = TreeNode("MAX", current_depth)

        for col in valid_moves:
            expected_value, chance_node = _calculate_expected_value_tree(board, depth, col, utils, current_depth + 1)
            node.add_child(chance_node)
            if expected_value > max_score:
                max_score = expected_value
                best_col = col
        node.score = max_score
        node.col = best_col
        return max_score, best_col, node

    else:
        min_score = float('inf')
        best_col = None
        node = TreeNode("MIN", current_depth)

        for col in valid_moves:
            board.drop_piece(col, player)
            val, _, child_node = _expectiminimax_recursive(board, depth - 1, True, utils, current_depth + 1)
            board.undo_move()
            node.add_child(child_node)
            if val < min_score:
                min_score = val
                best_col = col
        node.score = min_score
        node.col = best_col
        return min_score, best_col, node


def _calculate_expected_value_tree(board: Board, depth, chosen_col, utils, current_depth):
    """Chance node evaluation"""
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
        value, _, child_node = _expectiminimax_recursive(board, depth - 1, False, utils, current_depth + 1)
        board.undo_move()

        prob_node = TreeNode("CHANCE", current_depth + 1, col=landing_col, score=value, probability=prob)
        prob_node.add_child(child_node)
        chance_node.add_child(prob_node)

        total_expected_value += prob * value

    chance_node.score = total_expected_value
    return total_expected_value, chance_node


def print_tree(node: TreeNode, board: Board, indent=""):
    """Print the tree recursively with board snapshots"""
    node_type = node.node_type
    col_info = f" [Col {node.col}]" if node.col is not None else ""
    score_info = f" Score: {node.score:.2f}" if node.score is not None else ""
    prob_info = f" (p={node.probability:.2f})" if node.probability is not None else ""

    print(f"{indent}{node_type}{col_info}{score_info}{prob_info}")

    # Print board at this node
    if hasattr(board, "print_bitboard"):
        print(f"{indent}Board state:")
        board.print_bitboard(indent + "  ")

    for child in node.children:
        print_tree(child, board, indent + "    ")
