# 1 --> empty , 2 --> human , 3 --> ai
class board :
   def __init__(self , state):
        if state is None:
            self.state = int('1' * 42)  # 42 cells empty
        else:
            self.state = state
   def isEmpty(self):
         if self.state == int('1' * 42):  # 42 cells, all empty
            return True
         return False
   def set_cell(self ,state , index , player):
        s = list(str(self.state).zfill(42))
        if s[index] == '1':  # only empty cells
            s[index] = str(self.currentPlayer)
            self.state = int(''.join(s))
            
     # Reset board
   def reset(self):
        self.state = int('1' * 42)
    