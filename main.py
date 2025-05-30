"""
Main entry point for the Word Search Game
"""

import pygame
import sys
from game import WordSearchGame

def main():
    """Initialize and run the word search game"""
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Word Search Game")
    
    # Initialize the game
    game = WordSearchGame(screen)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
