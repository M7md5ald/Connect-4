from board import board
ROWS = 6 
COLS= 7
class utils :
    def __init__(self ):
      pass
        

    def get_child(self , board , player) :
        children =[]
        for move in  self.valid_move( board) :
            new_board =  board.copy()
            self.apply_move(new_board , move , player)
            children.append(new_board)
        return children
            
    def valid_move (self , board ):
        s= str(board.state)
        moves = [col for col in range(COLS) if s[col] == '1']  # top row empty
        return moves
    
    def apply_move(self , board , index , player) :
        s = list(str(board.state)) 
        for row in range(ROWS - 1, -1, -1):
            idx = row * COLS + index 
            if s[idx] == '1':
             s[idx] = str(player) 
             board.state = int(''.join(s)) 
             return 
        
    
    def is_full(self , board ):
        s = str(board.state)
        if '1' not in s: 
            return True
        return False
    def is_terminal(self , board  , k ):
        return self.is_full(board) or k== 0
  
    def check_win(self, board, player):
      
        s = str(board.state)
        p = str(player)
        
        # Check horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                idx = row * COLS + col
                if all(s[idx + i] == p for i in range(4)):
                    return True
        
        # Check vertical
        for row in range(ROWS - 3):
            for col in range(COLS):
                idx = row * COLS + col
                if all(s[idx + i * COLS] == p for i in range(4)):
                    return True
        
        # Check diagonal (down-right)
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                idx = row * COLS + col
                if all(s[idx + i * (COLS + 1)] == p for i in range(4)):
                    return True
        
        # Check diagonal (down-left)
        for row in range(ROWS - 3):
            for col in range(3, COLS):
                idx = row * COLS + col
                if all(s[idx + i * (COLS - 1)] == p for i in range(4)):
                    return True
        
        return False