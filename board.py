empty = 0
player = 1
AI = 2

rows = 6
cols = 7

class Board:
    def __init__(self):
        self.board = [[empty for n in range(cols)] for n in range(rows)]
        
        self.column_heights = [0] * cols # keeps track of the top of each column
        
        self.move_history = [] # needed for unde_move method

    def drop_piece(self, col, piece):
        row = self.column_heights[col]

        self.board[row][col] = piece
        
        self.column_heights[col] += 1
        
        self.move_history.append(col)
        
    def undo_move(self): # method used to back track after exploring different possibilities (not actually used in game)
        col = self.move_history.pop()
        
        self.column_heights[col] -= 1
        
        row = self.column_heights[col]
        
        self.board[row][col] = empty

    def is_valid_location(self, col):
        return self.column_heights[col] < rows

    def get_valid_moves(self):
        moves = []
        for col in range(cols):
            if self.is_valid_location(col):
                moves.append(col)
        return moves