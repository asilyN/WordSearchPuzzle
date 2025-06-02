"""
Word grid generation and management using Rabin-Karp algorithm
"""

import random
import time
from rabin_karp import RabinKarp

class WordGrid:
    def __init__(self, size, word_list, word_count):
        self.size = size
        self.word_list = word_list
        self.word_count = word_count
        self.grid = []
        self.placed_words = []
        self.word_positions = {}  # Maps word to list of positions
        self.found_positions = set()  # Positions of found words
        self.incorrect_positions = {}  # Maps positions to their timestamp
        self.rabin_karp = RabinKarp()
        
        # Direction vectors for word placement
        self.directions = [
            (0, 1),   # Right
            (1, 0),   # Down
            (1, 1),   # Diagonal down-right
            (0, -1),  # Left
            (-1, 0),  # Up
            (-1, -1), # Diagonal up-left
            (1, -1),  # Diagonal down-left
            (-1, 1)   # Diagonal up-right
        ]
    
    def generate(self):
        """Generate the word search grid"""
        self._initialize_grid()
        self._place_words()
        self._fill_empty_cells()
    
    def _initialize_grid(self):
        """Initialize empty grid"""
        self.grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.placed_words = []
        self.word_positions = {}
        self.found_positions = set()
    
    def _place_words(self):
        """Place words in the grid using Rabin-Karp for overlap detection"""
        # Select random words from the word list
        selected_words = random.sample(self.word_list, min(self.word_count, len(self.word_list)))
        
        for word in selected_words:
            word = word.upper()
            placed = False
            attempts = 0
            max_attempts = 100
            
            while not placed and attempts < max_attempts:
                # Choose random position and direction
                row = random.randint(0, self.size - 1)
                col = random.randint(0, self.size - 1)
                direction = random.choice(self.directions)
                
                if self._can_place_word(word, row, col, direction):
                    self._place_word(word, row, col, direction)
                    placed = True
                
                attempts += 1
            
            if placed:
                self.placed_words.append(word)
    
    def _can_place_word(self, word, start_row, start_col, direction):
        """Check if a word can be placed at the given position and direction"""
        dr, dc = direction
        
        # Check if word fits in grid
        end_row = start_row + (len(word) - 1) * dr
        end_col = start_col + (len(word) - 1) * dc
        
        if (end_row < 0 or end_row >= self.size or 
            end_col < 0 or end_col >= self.size):
            return False
        
        # Check for conflicts with existing letters
        for i, letter in enumerate(word):
            row = start_row + i * dr
            col = start_col + i * dc
            
            if self.grid[row][col] != ' ' and self.grid[row][col] != letter:
                return False
        
        # Use Rabin-Karp to check for unwanted word overlaps
        if self._creates_unwanted_overlap(word, start_row, start_col, direction):
            return False
        
        return True
    
    def _creates_unwanted_overlap(self, word, start_row, start_col, direction):
        """Use Rabin-Karp to detect unwanted word overlaps"""
        dr, dc = direction
        
        # Create a temporary grid with the word placed
        temp_grid = [row[:] for row in self.grid]
        for i, letter in enumerate(word):
            row = start_row + i * dr
            col = start_col + i * dc
            temp_grid[row][col] = letter
        
        # Check all directions for unwanted words formed
        for check_dir in self.directions:
            if self._check_direction_for_unwanted_words(temp_grid, check_dir):
                return True
        
        return False
    
    def _check_direction_for_unwanted_words(self, grid, direction):
        """Check a specific direction for unwanted word formations"""
        dr, dc = direction
        
        # Check each possible starting position
        for start_row in range(self.size):
            for start_col in range(self.size):
                # Extract string in this direction
                text = ""
                row, col = start_row, start_col
                
                while (0 <= row < self.size and 0 <= col < self.size and 
                       grid[row][col] != ' '):
                    text += grid[row][col]
                    row += dr
                    col += dc
                
                # Skip if text is too short or is one of our intended words
                if len(text) < 3 or text in self.placed_words:
                    continue
                
                # Use Rabin-Karp to check if this forms any unintended words
                if self.rabin_karp.contains_unwanted_pattern(text):
                    return True
        
        return False
    
    def _place_word(self, word, start_row, start_col, direction):
        """Place a word in the grid and record its positions"""
        dr, dc = direction
        positions = []
        
        for i, letter in enumerate(word):
            row = start_row + i * dr
            col = start_col + i * dc
            self.grid[row][col] = letter
            positions.append((row, col))
        
        self.word_positions[word] = positions
    
    def _fill_empty_cells(self):
        """Fill empty cells with random letters"""
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == ' ':
                    self.grid[row][col] = random.choice(letters)
    
    def is_word_at_positions(self, positions):
        """Check if the given positions form a valid word using Rabin-Karp"""
        if not positions:
            return False
        
        # Get the word formed by these positions
        word = ""
        for row, col in positions:
            if 0 <= row < self.size and 0 <= col < self.size:
                word += self.grid[row][col]
            else:
                return False
        
        # Check if this word (or its reverse) is in our placed words
        word_upper = word.upper()
        word_reverse = word_upper[::-1]
        
        # Use Rabin-Karp for efficient pattern matching
        for placed_word in self.placed_words:
            if (self.rabin_karp.search(placed_word, word_upper) or 
                self.rabin_karp.search(placed_word, word_reverse)):
                # Verify positions match exactly
                if self._verify_word_positions(placed_word, positions):
                    return True
        
        return False
    
    def _verify_word_positions(self, word, positions):
        """Verify that positions exactly match a placed word"""
        if word not in self.word_positions:
            return False
        
        word_pos = self.word_positions[word]
        
        # Check forward match
        if len(positions) == len(word_pos):
            if positions == word_pos:
                return True
            # Check reverse match
            if positions == word_pos[::-1]:
                return True
        
        return False
    
    def mark_word_found(self, positions):
        """Mark positions as found"""
        for pos in positions:
            self.found_positions.add(pos)
    
    def is_position_found(self, row, col):
        """Check if a position is part of a found word"""
        return (row, col) in self.found_positions
    
    def get_letter(self, row, col):
        """Get letter at specific position"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None
    
    def get_word_list(self):
        """Get list of words to find"""
        return self.placed_words.copy()
    
    def is_valid_selection(self, selected_cells):
        """Check if the selected cells form a valid word"""
        # Extract letters from selected cells
        word = ''
        for row, col in selected_cells:
            if 0 <= row < self.size and 0 <= col < self.size:  # Ensure coordinates are within bounds
                word += self.grid[row][col]
            else:
                return False  # Invalid selection if any cell is out of bounds

        # Check if the word exists in the placed words
        return word in self.placed_words
    
    def mark_word_incorrect(self, positions):
        """Mark positions as incorrect with current timestamp"""
        current_time = time.time()
        for pos in positions:
            self.incorrect_positions[pos] = current_time
    
    def is_position_incorrect(self, row, col):
        """Check if a position is part of an incorrect selection and clear old ones"""
        current_time = time.time()
        pos = (row, col)
        
        # Clear old incorrect positions (older than 500ms)
        positions_to_remove = []
        for position, timestamp in self.incorrect_positions.items():
            if current_time - timestamp > 0.5:  # 500ms = 0.5 seconds
                positions_to_remove.append(position)
        
        # Remove old positions
        for position in positions_to_remove:
            del self.incorrect_positions[position]
        
        return pos in self.incorrect_positions
