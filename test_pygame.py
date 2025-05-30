import pygame
import sys

def test_pygame():
    """Simple test to check if pygame works"""
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Test Window")
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.fill((100, 150, 200))
            
            # Draw a simple test message
            font = pygame.font.Font(None, 36)
            text = font.render("Pygame Test - Press ESC to close", True, (255, 255, 255))
            text_rect = text.get_rect(center=(400, 300))
            screen.blit(text, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("Pygame test completed successfully")
        
    except Exception as e:
        print(f"Pygame test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_pygame()