"""
Main game logic and state management for Word Search Game
"""

import pygame
import time
import json
from enum import Enum
from grid import WordGrid
from ui import UI
from leaderboard import Leaderboard
from word_lists import get_words_by_difficulty, WORD_LISTS

class GameState(Enum):
    START_SCREEN = 1
    NAME_INPUT = 2
    PLAYING = 3
    LEVEL_COMPLETE = 4
    GAME_COMPLETE = 5
    LEADERBOARD = 6

class WordSearchGame:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.START_SCREEN
        self.ui = UI(screen)
        self.leaderboard = Leaderboard()
        
        # Initialize pygame mixer for sound
        pygame.mixer.init()
        self.background_music = "sounds/442911__scicodedev__calm_happy_rpgtownbackground.mp3"
        pygame.mixer.music.load(self.background_music)
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        
        # Load sound effects
        self.wrong_sound = pygame.mixer.Sound("sounds/325443__troym1__wrong.mp3")
        self.wrong_sound.set_volume(0.7)  # Set volume to 70%
        self.click_sound = pygame.mixer.Sound("sounds/170928__zeditez__mouse-click (mp3cut.net).wav")
        self.click_sound.set_volume(0.5)  # Set volume to 50%
        self.correct_sound = pygame.mixer.Sound("sounds/335908__littlerainyseasons__correct.mp3")
        self.correct_sound.set_volume(0.7)  # Set volume to 70%
        
        # Game variables
        self.player_name = ""
        self.current_level = 1
        self.max_level = 5
        self.grid = None
        self.start_time = 0
        self.total_score = 0
        self.level_scores = [] # Stores individual scores for each level
        self.level_completion_times = [] # Stores completion times for each level
        self.current_level_completion_time_for_display = 0 # Added for pausing timer display
        
        # Selection variables
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.found_words = set()
        
        # Level configurations
        self.level_configs = {
            1: {"size": 5, "word_count": 3, "word_list": "easy"},
            2: {"size": 7, "word_count": 4, "word_list": "easy"},
            3: {"size": 10, "word_count": 6, "word_list": "medium"},
            4: {"size": 12, "word_count": 8, "word_list": "medium"},
            5: {"size": 15, "word_count": 10, "word_list": "hard"}
        }
    
    def handle_event(self, event):
        """Handle pygame events based on current game state"""
        if event.type == pygame.KEYDOWN:
            # Add music control with 'M' key
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            # Add music restart with 'R' key
            elif event.key == pygame.K_r:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(-1)
        
        if self.state == GameState.START_SCREEN:
            self._handle_start_screen_event(event)
        elif self.state == GameState.NAME_INPUT:
            self._handle_name_input_event(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_event(event)
        elif self.state == GameState.LEVEL_COMPLETE:
            self._handle_level_complete_event(event)
        elif self.state == GameState.GAME_COMPLETE:
            self._handle_game_complete_event(event)
        elif self.state == GameState.LEADERBOARD:
            self._handle_leaderboard_event(event)
    
    def _handle_start_screen_event(self, event):
        """Handle events on the start screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.state = GameState.NAME_INPUT
            elif event.key == pygame.K_l:
                self.click_sound.play()
                self.state = GameState.LEADERBOARD
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.ui.is_button_clicked(mouse_pos, "start"):
                self.click_sound.play()
                self.state = GameState.NAME_INPUT
            elif self.ui.is_button_clicked(mouse_pos, "leaderboard"):
                self.click_sound.play()
                self.state = GameState.LEADERBOARD
    
    def _handle_name_input_event(self, event):
        """Handle name input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.player_name.strip():
                self.click_sound.play()
                self._start_level(1)
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.click_sound.play()
                self.state = GameState.START_SCREEN
            elif event.unicode.isprintable() and len(self.player_name) < 20:
                self.player_name += event.unicode
    
    def _handle_playing_event(self, event):
        """Handle gameplay events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.click_sound.play()
                mouse_pos = pygame.mouse.get_pos()
                grid_pos = self.ui.screen_to_grid(mouse_pos)
                # Ensure clicks outside the grid are ignored
                if grid_pos is None:
                    return
                
                self.selecting = True
                self.selection_start = grid_pos
                self.selection_end = grid_pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selecting:
                self.selecting = False
                self._check_word_selection()
        
        elif event.type == pygame.MOUSEMOTION and self.selecting:
            mouse_pos = pygame.mouse.get_pos()
            grid_pos = self.ui.screen_to_grid(mouse_pos)
            if grid_pos:
                self.selection_end = grid_pos
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.click_sound.play()
                self._save_current_progress_if_any() # Save progress before resetting
                self.state = GameState.START_SCREEN
                self._reset_game()
    
    def _handle_level_complete_event(self, event):
        """Handle level completion events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                if self.current_level < self.max_level:
                    self._start_level(self.current_level + 1)
                else:
                    self._complete_game()
            elif event.key == pygame.K_ESCAPE:
                self.click_sound.play()
                self._save_current_progress_if_any() # Save progress before resetting
                self.state = GameState.START_SCREEN
                self._reset_game()
    
    def _handle_game_complete_event(self, event):
        """Handle game completion events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.state = GameState.START_SCREEN
                self._reset_game()
            elif event.key == pygame.K_l:
                self.click_sound.play()
                self.state = GameState.LEADERBOARD
    
    def _handle_leaderboard_event(self, event):
        """Handle leaderboard events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.state = GameState.START_SCREEN
    
    def _start_level(self, level):
        """Initialize a new level"""
        self.current_level = level
        config = self.level_configs[level]
        
        # Get words for this level
        word_list = get_words_by_difficulty(config["word_list"])
        
        # Create grid
        self.grid = WordGrid(config["size"], word_list, config["word_count"])
        self.grid.generate()
        
        # Reset level state
        self.found_words = set()
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.start_time = time.time()
        
        # Ensure background music is playing
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        
        self.state = GameState.PLAYING
    
    def _check_word_selection(self):
        """Check if the current selection matches a word"""
        if not (self.selection_start and self.selection_end):
            return

        # Get the selected path
        selected_positions = self._get_selection_path()
        if not selected_positions:
            return

        # Get the word from selected positions
        if not self.grid:
            return

        selected_word = ""
        # Validate positions before accessing the grid
        for pos in selected_positions:
            row, col = pos
            if not (0 <= row < self.grid.size and 0 <= col < self.grid.size):
                return  # Ignore invalid selections
            selected_word += self.grid.grid[row][col]

        # Check if this word exists in the grid (forward or backward)
        if self.grid.is_word_at_positions(selected_positions):
            word = selected_word.upper()
            if word not in self.found_words:
                self.correct_sound.play()  # Play correct sound when word is found
                self.found_words.add(word)
                self.grid.mark_word_found(selected_positions)

                # Check if level is complete
                if len(self.found_words) >= len(self.grid.placed_words):
                    self._complete_level()
        else:
            # Play wrong sound effect and mark cells red for incorrect answer
            if self.selection_start and self.selection_end:
                self.wrong_sound.play()
                self.grid.mark_word_incorrect(selected_positions)
        
        # Clear the selection after checking
        self.selection_start = None
        self.selection_end = None
    
    def _get_selection_path(self):
        """Get the path of positions from selection start to end"""
        if not (self.selection_start and self.selection_end):
            return []
        
        start_row, start_col = self.selection_start
        end_row, end_col = self.selection_end
        
        # Calculate direction
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        
        # Ensure it's a straight line (horizontal, vertical, or diagonal)
        if row_diff != 0 and col_diff != 0:
            if abs(row_diff) != abs(col_diff):
                return []  # Not a valid diagonal
        
        # Generate path
        positions = []
        steps = max(abs(row_diff), abs(col_diff))
        
        if steps == 0:
            return [self.selection_start]
        
        row_step = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
        
        for i in range(steps + 1):
            row = start_row + i * row_step
            col = start_col + i * col_step
            positions.append((row, col))
        
        return positions
    
    def _complete_level(self):
        """Handle level completion"""
        actual_completion_time = time.time() - self.start_time # Capture actual time
        self.current_level_completion_time_for_display = actual_completion_time # Store for display

        level_score = self._calculate_score(actual_completion_time) # Use actual time for score
        self.level_scores.append(level_score)
        self.level_completion_times.append(actual_completion_time) # Store completion time
        self.total_score += level_score
        
        # Leaderboard saving is now handled by _complete_game or when quitting
            
        self.state = GameState.LEVEL_COMPLETE
    
    def _complete_game(self):
        """Handle game completion"""
        # Calculate final rank based on average completion time for all levels
        avg_time = float('inf')
        if self.level_completion_times:
            avg_time = sum(self.level_completion_times) / len(self.level_completion_times)
        rank = self._get_rank(avg_time)
        
        # Save final score to leaderboard (leaderboard handles sorting/duplicates)
        if self.player_name.strip():
            self.leaderboard.add_score(self.player_name, self.total_score, rank)
        
        self.state = GameState.GAME_COMPLETE

    def _save_current_progress_if_any(self):
        """Saves the current game progress to the leaderboard if applicable."""
        if self.player_name.strip() and self.level_completion_times:
            # Calculate current rank based on average completion time so far
            current_avg_time = sum(self.level_completion_times) / len(self.level_completion_times)
            current_rank = self._get_rank(current_avg_time)
            
            # Add current progress to leaderboard
            self.leaderboard.add_score(self.player_name, self.total_score, current_rank)

    def _calculate_score(self, completion_time):
        """Calculate score based on completion time"""
        base_score = 1000
        time_penalty = min(completion_time * 10, 800)  # Max penalty of 800
        return max(int(base_score - time_penalty), 200)  # Minimum score of 200
    
    def _get_rank(self, avg_time):
        """Get rank based on average completion time and current level"""
        # Base time thresholds for each rank
        base_thresholds = {
            "S": 30,
            "A": 60,
            "B": 90,
            "C": 120
        }
        
        # Adjust thresholds based on level (higher level = stricter time requirements)
        level_multiplier = 1.0 - (self.current_level - 1) * 0.1  # Each level reduces time by 10%
        level_multiplier = max(0.5, level_multiplier)  # Minimum multiplier of 0.5
        
        # Calculate adjusted thresholds
        adjusted_thresholds = {
            rank: threshold * level_multiplier 
            for rank, threshold in base_thresholds.items()
        }
        
        # Determine rank based on adjusted thresholds
        if avg_time < adjusted_thresholds["S"]:
            return "S"
        elif avg_time < adjusted_thresholds["A"]:
            return "A"
        elif avg_time < adjusted_thresholds["B"]:
            return "B"
        elif avg_time < adjusted_thresholds["C"]:
            return "C"
        else:
            return "D"
    
    def _reset_game(self):
        """Reset game to initial state"""
        self.player_name = ""
        self.current_level = 1
        self.total_score = 0
        self.level_scores = []
        self.level_completion_times = [] # Reset completion times
        self.grid = None
        self.found_words = set()
        
        # Restart background music
        pygame.mixer.music.stop()
        pygame.mixer.music.play(-1)
    
    def update(self):
        """Update game state"""
        pass
    
    def draw(self):
        """Draw the current game state"""
        self.screen.fill((240, 240, 240))
        
        if self.state == GameState.START_SCREEN:
            self.ui.draw_start_screen()
        elif self.state == GameState.NAME_INPUT:
            self.ui.draw_name_input(self.player_name)
        elif self.state == GameState.PLAYING:
            current_time = time.time() - self.start_time
            self.ui.draw_game_screen(
                self.grid, self.found_words, self.selection_start, 
                self.selection_end, self.current_level, current_time
            )
        elif self.state == GameState.LEVEL_COMPLETE:
            # Use the stored completion time for display
            score = self.level_scores[-1] if self.level_scores else 0
            self.ui.draw_level_complete(self.current_level, self.current_level_completion_time_for_display, score)
        elif self.state == GameState.GAME_COMPLETE:
            avg_time = sum(self.level_scores) / len(self.level_scores) if self.level_scores else 0
            rank = self._get_rank(avg_time)
            self.ui.draw_game_complete(self.total_score, rank)
        elif self.state == GameState.LEADERBOARD:
            scores = self.leaderboard.get_top_scores()
            self.ui.draw_leaderboard(scores)
