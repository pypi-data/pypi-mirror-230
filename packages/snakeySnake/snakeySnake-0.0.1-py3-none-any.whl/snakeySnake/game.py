import time
import random
import pygame
import pathlib

from snakeySnake.snake import Snake, Direction
from snakeySnake.scoreboard import ScoreBoard

class Game:
    def __init__(self):
        self.displaySize = 600

        self.scoreBoard = ScoreBoard()
        self.snake = Snake(self.displaySize/2, 
                           0.1, 
                           self.scoreBoard.addTimeSurvived, 
                           self.scoreBoard.addAppleCollected)
        self.lastUpdateTime = time.perf_counter()
        self.lastAppleTime = time.perf_counter()

        self.appleSize = self.snake.size * 2
        self.appleLocations = []
        self.gameOver = False
        self.exit = False

    def run(self):
        # Initialise board
        pygame.init()
        display = pygame.display.set_mode((self.displaySize, self.displaySize))
        pygame.display.update()
        pygame.display.set_caption('Snake Game')

        appleImage = pygame.image.load(str(pathlib.Path(__file__).parent.absolute()) + "/data/apple.png").convert()
        appleImage = pygame.transform.scale(appleImage, (self.appleSize, self.appleSize))

        while (not self.exit):
            for event in pygame.event.get():
                # Quit game
                if (event.type == pygame.QUIT):
                    self.exit = True

            while (not self.gameOver):
                for event in pygame.event.get():
                    # Move snake based on key movements
                    if (event.type == pygame.KEYDOWN):
                        direction = Direction.NONE
                        if ((event.key == pygame.K_w) or
                            (event.key == pygame.K_UP)):
                            direction = Direction.UP
                        elif ((event.key == pygame.K_s) or
                            (event.key == pygame.K_DOWN)):
                            direction = Direction.DOWN
                        elif ((event.key == pygame.K_a) or
                            (event.key == pygame.K_LEFT)):
                            direction = Direction.LEFT
                        elif ((event.key == pygame.K_d) or
                            (event.key == pygame.K_RIGHT)):
                            direction = Direction.RIGHT
                
                        self.snake.move(direction)
                self.snake.update(self.appleLocations)

                display.fill("black")

                self._drawApples(display, appleImage)
                self.snake.draw(display)
                self.scoreBoard.displayCurrentScore(display)

                self._checkGameOver(display)
                pygame.display.update()
        
        pygame.quit()
        quit()
    
    def _drawApples(self, display, appleImage):
        if time.perf_counter() - self.lastAppleTime > 5.0:
            self.lastAppleTime = time.perf_counter()
            self.appleLocations.append((random.randint(0, self.displaySize - self.appleSize),
                                        random.randint(0, self.displaySize - self.appleSize)))

        for apple in self.appleLocations:
            display.blit(appleImage, apple)

    def _checkGameOver(self, display):
        x = self.snake.getHeadX()
        y = self.snake.getHeadY()

        if (x >= self.displaySize or
            x <= 0 or
            y >= self.displaySize or
            y <= 0 or
            self.snake.ranIntoItself()):

            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Game Over', 
                               True, 
                               "white")
            textRect = text.get_rect()
            textRect.center = [self.displaySize/2, self.displaySize/3]
            display.blit(text, textRect)

            self.scoreBoard.writeToFile()
            self.scoreBoard.displayPastScores(display)
            self.gameOver = True
