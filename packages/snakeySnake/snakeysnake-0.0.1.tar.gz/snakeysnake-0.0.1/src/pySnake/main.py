import sys
import os
sys.path.append(os.getcwd() + "/src")

from game import Game

if __name__ == "__main__":
    snakeGame = Game()
    snakeGame.run()