"""
User interface components for Word Search Game
"""

import pygame
import math

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.colors = {
            'background': (255,255,255),
            'grid_bg': (255, 255, 255),
            'grid_border': (139, 125, 107, 255),
            'letter': (139, 69, 19, 255),
            'found_word': (205, 149, 12, 255),
            'selection':  (255, 211, 155, 255),
            'button': (139, 62, 47, 255),
            'button_hover': (100, 149, 237),
            'text': (139, 131, 120, 255),
            'title': (139, 69, 19, 255),
            'score': (0, 100, 0),
            'incorrect': (255, 64, 64, 255)
        }
        
        # Fonts
        pygame.font.init()
        self.fonts = {
            'title': pygame.font.Font('fonts/PressStart2P-Regular.ttf', 50), # Changed to use Fredoka font
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font('fonts/Fredoka-Regular.ttf', 24),
            'small': pygame.font.Font(None, 24)
        }
        
        # Grid display settings
        self.grid_start_x = 50
        self.grid_start_y = 100
        self.cell_size = 30
        
        # Button settings
        self.button_width = 200
        self.button_height = 50

        self.incorrect_selections = []  # Track incorrect selections with expiration times
    
    def draw_start_screen(self):
        """Draw the start screen"""
        # Title
        title_text = self.fonts['title'].render("WORD SEARCH", True, self.colors['title'])
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Find all hidden words in the grid!",
            "",
            "5 Levels of increasing difficulty",
            "Faster completion = Higher rank!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.fonts['medium'].render(instruction, True, self.colors['text'])
            text_rect = text.get_rect(center=(self.width // 2, 250 + i * 30))
            self.screen.blit(text, text_rect)
        
        # Start button
        start_button_rect = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            400,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.colors['button'], start_button_rect)
        pygame.draw.rect(self.screen, self.colors['grid_border'], start_button_rect, 2)
        
        start_text = self.fonts['large'].render("START GAME", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Leaderboard button
        leaderboard_button_rect = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            480,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.colors['button'], leaderboard_button_rect)
        pygame.draw.rect(self.screen, self.colors['grid_border'], leaderboard_button_rect, 2)
        
        leaderboard_text = self.fonts['large'].render("LEADERBOARD", True, (255, 255, 255))
        leaderboard_text_rect = leaderboard_text.get_rect(center=leaderboard_button_rect.center)
        self.screen.blit(leaderboard_text, leaderboard_text_rect)
        
    
    def draw_name_input(self, name):
        """Draw the name input screen"""
        # Title
        title_text = self.fonts['title'].render("ENTER YOUR NAME", True, self.colors['title'])
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Name input box
        input_box = pygame.Rect(self.width // 2 - 150, 300, 300, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box)
        pygame.draw.rect(self.screen, self.colors['grid_border'], input_box, 2)
        
        # Name text
        name_text = self.fonts['large'].render(name, True, self.colors['text'])
        name_rect = name_text.get_rect(left=input_box.left + 10, centery=input_box.centery)
        self.screen.blit(name_text, name_rect)
        
        # Cursor
        if len(name) > 0:
            cursor_x = name_rect.right + 2
        else:
            cursor_x = input_box.left + 10
        pygame.draw.line(self.screen, self.colors['text'], 
                        (cursor_x, input_box.top + 10), 
                        (cursor_x, input_box.bottom - 10), 2)
        
        # Instructions
        instruction_text = self.fonts['medium'].render("Press ENTER to continue or ESC to go back", True, self.colors['text'])
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, 400))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_game_screen(self, grid, found_words, selection_start, selection_end, level, current_time):
        """Draw the main game screen"""
        # Level info
        level_text = self.fonts['large'].render(f"LEVEL {level}", True, self.colors['title'])
        self.screen.blit(level_text, (20, 20))
        
        # Timer
        time_text = self.fonts['medium'].render(f"Time: {current_time:.1f}s", True, self.colors['text'])
        self.screen.blit(time_text, (20, 60))
        
        # Words found counter
        total_words = len(grid.get_word_list())
        found_count = len(found_words)
        progress_text = self.fonts['medium'].render(f"Words: {found_count}/{total_words}", True, self.colors['text'])
        self.screen.blit(progress_text, (200, 60))
        
        # Draw grid
        self._draw_grid(grid, selection_start, selection_end)
        
        # Draw word list
        self._draw_word_list(grid.get_word_list(), found_words)
        
        # Instructions
        instruction_text = self.fonts['small'].render("Click and drag to select words. ESC to quit.", True, self.colors['text'])
        self.screen.blit(instruction_text, (20, self.height - 30))
    
    def _draw_grid(self, grid, selection_start, selection_end):
        """Draw the word search grid without selection highlighting"""
        grid_size = grid.size
        total_grid_width = grid_size * self.cell_size
        total_grid_height = grid_size * self.cell_size

        # Center the grid
        start_x = (self.width - total_grid_width) // 2
        start_y = 120

        # Update grid position for mouse interaction
        self.grid_start_x = start_x
        self.grid_start_y = start_y

        # Get selected cells if there's a selection
        selected_cells = []
        if selection_start and selection_end:
            selected_cells = self._get_selected_cells(selection_start, selection_end)

        # Draw grid cells
        for row in range(grid_size):
            for col in range(grid_size):
                x = start_x + col * self.cell_size
                y = start_y + row * self.cell_size

                # Cell background
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                # Color based on state
                if grid.is_position_found(row, col):
                    color = self.colors['found_word']
                elif grid.is_position_incorrect(row, col):
                    color = self.colors['incorrect']
                elif (row, col) in selected_cells:
                    color = self.colors['selection']
                else:
                    color = self.colors['grid_bg']

                pygame.draw.rect(self.screen, color, cell_rect)
                pygame.draw.rect(self.screen, self.colors['grid_border'], cell_rect, 1)

                # Letter
                letter = grid.get_letter(row, col)
                if letter:
                    letter_text = self.fonts['medium'].render(letter, True, self.colors['letter'])
                    letter_rect = letter_text.get_rect(center=cell_rect.center)
                    self.screen.blit(letter_text, letter_rect)

    def _get_selected_cells(self, start_pos, end_pos):
        """Calculate all cells between start and end positions for highlighting"""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        selected_cells = []
        
        # Determine direction of selection
        row_step = 1 if end_row >= start_row else -1
        col_step = 1 if end_col >= start_col else -1
        
        # Vertical selection
        if start_col == end_col:
            for row in range(start_row, end_row + row_step, row_step):
                selected_cells.append((row, start_col))
        
        # Horizontal selection
        elif start_row == end_row:
            for col in range(start_col, end_col + col_step, col_step):
                selected_cells.append((start_row, col))
        
        # Diagonal selection (45 degrees only)
        elif abs(end_row - start_row) == abs(end_col - start_col):
            for i in range(abs(end_row - start_row) + 1):
                row = start_row + i * row_step
                col = start_col + i * col_step
                selected_cells.append((row, col))
        
        return selected_cells
    
    def _draw_word_list(self, word_list, found_words):
        """Draw the list of words to find"""
        # Position word list on the right side
        start_x = self.width - 260
        start_y = 120
        
        title_text = self.fonts['medium'].render("FIND THESE WORDS:", True, self.colors['title'])
        self.screen.blit(title_text, (start_x, start_y))
        
        for i, word in enumerate(word_list):
            y = start_y + 40 + i * 25
            
            # Color based on whether word is found
            if word in found_words:
                color = self.colors['score']
                # Strike through effect
                word_text = self.fonts['small'].render(f"✓ {word}", True, color)
            else:
                color = self.colors['text']
                word_text = self.fonts['small'].render(f"• {word}", True, color)
            
            self.screen.blit(word_text, (start_x, y))
    
    def draw_level_complete(self, level, completion_time, score):
        """Draw level completion screen"""
        # Background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.fonts['title'].render(f"LEVEL {level} COMPLETE!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Stats
        time_text = self.fonts['large'].render(f"Time: {completion_time:.1f} seconds", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.width // 2, 280))
        self.screen.blit(time_text, time_rect)
        
        score_text = self.fonts['large'].render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, 320))
        self.screen.blit(score_text, score_rect)
        
        # Rank
        rank = self._get_time_rank(completion_time)
        rank_text = self.fonts['title'].render(f"RANK: {rank}", True, self._get_rank_color(rank))
        rank_rect = rank_text.get_rect(center=(self.width // 2, 380))
        self.screen.blit(rank_text, rank_rect)
        
        # Continue instruction
        continue_text = self.fonts['medium'].render("Press SPACE to continue or ESC to quit", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.width // 2, 450))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_complete(self, total_score, rank):
        """Draw game completion screen"""
        # Background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.fonts['title'].render("GAME COMPLETE!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Final score
        score_text = self.fonts['large'].render(f"Total Score: {total_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        # Final rank
        rank_text = self.fonts['title'].render(f"FINAL RANK: {rank}", True, self._get_rank_color(rank))
        rank_rect = rank_text.get_rect(center=(self.width // 2, 320))
        self.screen.blit(rank_text, rank_rect)
        
        # Instructions
        instruction_text = self.fonts['medium'].render("Press SPACE to return to menu or L for leaderboard", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, 400))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_leaderboard(self, scores):
        """Draw the leaderboard screen"""
        # Title
        title_text = self.fonts['title'].render("LEADERBOARD", True, self.colors['title'])
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Header
        header_y = 180
        header_texts = ["RANK", "NAME", "SCORE", "GRADE"]
        header_positions = [200, 350, 500, 650]
        
        for text, x in zip(header_texts, header_positions):
            header_text = self.fonts['medium'].render(text, True, self.colors['title'])
            self.screen.blit(header_text, (x, header_y))
        
        # Scores
        start_y = 220
        for i, score_data in enumerate(scores[:10]):  # Top 10
            y = start_y + i * 30
            
            # Rank number
            rank_text = self.fonts['medium'].render(f"{i + 1}.", True, self.colors['text'])
            self.screen.blit(rank_text, (200, y))
            
            # Name
            name_text = self.fonts['medium'].render(score_data['name'], True, self.colors['text'])
            self.screen.blit(name_text, (350, y))
            
            # Score
            score_text = self.fonts['medium'].render(str(score_data['score']), True, self.colors['score'])
            self.screen.blit(score_text, (500, y))
            
            # Grade
            grade_color = self._get_rank_color(score_data['rank'])
            grade_text = self.fonts['medium'].render(score_data['rank'], True, grade_color)
            self.screen.blit(grade_text, (650, y))
        
        # Back instruction
        back_text = self.fonts['medium'].render("Press SPACE or ESC to return", True, self.colors['text'])
        back_rect = back_text.get_rect(center=(self.width // 2, 600))
        self.screen.blit(back_text, back_rect)
    
    def screen_to_grid(self, mouse_pos):
        """Convert screen coordinates to grid coordinates"""
        mouse_x, mouse_y = mouse_pos
        
        # Check if mouse is within grid bounds
        if (self.grid_start_x <= mouse_x < self.grid_start_x + self.cell_size * 20 and
            self.grid_start_y <= mouse_y < self.grid_start_y + self.cell_size * 20):
            
            col = (mouse_x - self.grid_start_x) // self.cell_size
            row = (mouse_y - self.grid_start_y) // self.cell_size
            
            return (row, col)
        
        return None
    
    def is_button_clicked(self, mouse_pos, button_type):
        """Check if a button was clicked"""
        mouse_x, mouse_y = mouse_pos
        
        if button_type == "start":
            button_rect = pygame.Rect(
                self.width // 2 - self.button_width // 2,
                400, # Adjusted to match draw_start_screen
                self.button_width,
                self.button_height
            )
            return button_rect.collidepoint(mouse_x, mouse_y)
        
        elif button_type == "leaderboard":
            button_rect = pygame.Rect(
                self.width // 2 - self.button_width // 2,
                480, # Adjusted to match draw_start_screen
                self.button_width,
                self.button_height
            )
            return button_rect.collidepoint(mouse_x, mouse_y)
        
        return False
    
    def _get_time_rank(self, time):
        """Get rank based on completion time"""
        if time < 30:
            return "S"
        elif time < 60:
            return "A"
        elif time < 90:
            return "B"
        elif time < 120:
            return "C"
        else:
            return "D"
    
    def _get_rank_color(self, rank):
        """Get color for rank display"""
        rank_colors = {
            'S': (255, 215, 0),    # Gold
            'A': (192, 192, 192),  # Silver
            'B': (205, 127, 50),   # Bronze
            'C': (139, 69, 19),    # Brown
            'D': (128, 128, 128)   # Gray
        }
        return rank_colors.get(rank, (255, 255, 255))
