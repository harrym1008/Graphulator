from enum import Enum
import pygame

hexLetters = "0123456789abcedf"

class Colour:
    def __init__(self, r, g, b, a=255) -> None:
        self.tuple = (r, g, b, a)
        self.colour = pygame.Color(r, g, b, a)
        self.faded = pygame.Color(r, g, b, int(a * 0.392))

        self.hex = '#%02x%02x%02x' % (r, g, b)
        


    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Colour):
            return __o.tuple == self.tuple
        return False



colours = {
    "black": Colour(0, 0, 0),
    "white": Colour(255, 255, 255),
    "grey": Colour(128, 128, 128),

    "red": Colour(255, 0, 0),
    "green": Colour(0, 255, 0),
    "blue": Colour(0, 0, 255),
    "light blue": Colour(0, 157, 255),
    "cyan": Colour(0, 255, 255),
    "magenta": Colour(255, 0, 255),
    "yellow": Colour(255, 255, 0),
    "dark yellow": Colour(247, 199, 45),
    "orange": Colour(255, 145, 0),

    "transparent": Colour(0, 0, 0, 0)
}



graphColours = [
    "red",
    "blue",
    "green",
    "magenta",
    "dark yellow",
    "light blue",
    "orange"
]




def GetColourForPlotIndex(index):
    index = index % len(graphColours)
    return colours[graphColours[index]]


colourMap = {
    colours["transparent"].tuple: 0,
    colours["red"].tuple: 1,
    colours["blue"].tuple: 2,
    colours["green"].tuple: 3,
    colours["magenta"].tuple: 4,
    colours["dark yellow"].tuple: 5,
    colours["dark yellow"].tuple: 6,
    colours["light blue"].tuple: 7,
    colours["orange"].tuple: 8,
    colours["white"].tuple: 9,
}