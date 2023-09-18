import pygame
import os

absolutePath = os.path.dirname(__file__)

class ScoreBoard:
    # Score:
    # + 250 points for every apple collected
    # + 5 points for every second survived
    def __init__(self):
        self.score = 0
        self.pastScores = []

    def addAppleCollected(self):
        self.score += 250
    
    def addTimeSurvived(self, time):
        self.score += 5 * time

    def writeToFile(self):
        with open(os.path.join(absolutePath, "data/scoreboard.txt"), "r") as fRead:
            line = fRead.readline()
            while line != '':
                self.pastScores.append(float(line.split(",")[1].strip()))
                line = fRead.readline()
            self.pastScores.append(round(self.score))
            self.pastScores.sort(reverse = True)
        
        with open(os.path.join(absolutePath, "data/scoreboard.txt"), "w") as fWrite:
            place = 1
            for score in self.pastScores:
                fWrite.write(str(place) + "," + str(round(score)) + "\n")
                place += 1

    def displayCurrentScore(self, display):
        font = pygame.font.Font('freesansbold.ttf', 20)
        text = font.render(str(int(self.score)), 
                           True, 
                           "white")
        textRect = text.get_rect()
        textRect.center = 30, 30
        display.blit(text, textRect)

    def displayPastScores(self, display):
        font = pygame.font.Font('freesansbold.ttf', 20)

        for idx in range(0, 5):
            if (abs(int(self.pastScores[idx]) - self.score) < 2):
                text = font.render(str(idx + 1) + ". " + str(int(self.pastScores[idx])), 
                                   True, 
                                   "green")
            else:
                text = font.render(str(idx + 1) + ". " + str(int(self.pastScores[idx])), 
                                   True, 
                                   "blue")
            textRect = text.get_rect()
            x, y = display.get_size()
            textRect.center = x/2, 5 * y/12 + 20*idx
            display.blit(text, textRect)