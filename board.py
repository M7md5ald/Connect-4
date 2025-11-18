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
from textwrap import indent

empty = 0
player = 1
AI = 2

rows = 6
cols = 7
WINDOW_LENGTH = 4


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
    def print_bitboard(board_obj, indent=""):
         """Print the board (2D array) in a readable format"""
         symbol_map = {empty: ".", player: "R", AI: "Y"}
         for row in reversed(board_obj.board):  # print top row last for Connect 4 style
            print(indent + " ".join(symbol_map[cell] for cell in row))
         print(indent + "-" * (2 * cols - 1))