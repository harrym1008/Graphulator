import pygame

hexLetters = "0123456789abcedf"

class Colour:
    def __init__(self, r, g, b, a=255) -> None:
        self.colour = pygame.Color(r, g, b, a)

        hexRGB = [r // 16, r % 16, g // 16, g % 16, b // 16, b % 16]
        self.hex = ""
        for value in hexRGB:
            self.hex += hexLetters[value]


colours = {
    "black": Colour(0, 0, 0),
    "white": Colour(250, 255, 255),

    "red": Colour(255, 0, 0),
    "green": Colour(0, 255, 0),
    "blue": Colour(0, 0, 255),
    "cyan": Colour(0, 255, 255),
    "magenta": Colour(255, 0, 255),
    "yellow": Colour(255, 255, 0),
    "darker yellow": Colour(247, 199, 45),

    "transparent": Colour(0, 0, 0, 0)
}