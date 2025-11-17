PROB_CHOSEN = 0.6
PROB_NEIGHBOR = 0.2
PROB_EDGE_NEIGHBOR = 0.4

def expectiminimax(board, depth, is_ai_turn):

    if depth == 0 or board.is_board_full():
        if board.is_board_full():
            return board.get_final_score()
        else:
            return board.heuristic_evaluation()

    # Layer 1: MAX Node (AI Chooses Column)
    if is_ai_turn: 
        max_expected_value = -float('inf')
        for chosen_col in board.get_valid_moves():
            
            # AI chooses a column, but the outcome is probabilistic so We call the CHANCE layer helper to get the expected value of this choice.
            expected_value = calculate_expected_value(board, depth, chosen_col)
            
            max_expected_value = max(max_expected_value, expected_value)

        return max_expected_value

    # Layer 3: MIN Node (Human Chooses Column)
    else:
        min_value = float('inf')
        for col in board.get_valid_moves():
            
            board.drop_piece(col, HUMAN)
            
            # Recurse (switches back to MAX layer, depth - 1)
            new_score = expectiminimax(board, depth - 1, True)
            
            board.undo_move()
            
            min_value = min(min_value, new_score)
        return min_value


# Layer 2: CHANCE Node
def calculate_expected_value(board, depth, chosen_col):    # Calculates the expected value (weighted average) of the AI choosing 'chosen_col',
    
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

    # --- Calculate the weighted average ---
    for landing_col, prob in outcomes:
        
        board.drop_piece(landing_col, AI)
        
        # 2. Recurse (Switches to MIN player, reduce depth)
        value_of_outcome = expectiminimax(board, depth - 1, False) 
        
        board.undo_move()
        
        total_expected_value += prob * value_of_outcome
        
    return total_expected_value