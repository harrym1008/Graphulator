from enum import Enum
import pygame

hexLetters = "0123456789abcedf"


# Generic class for storing colours for Pygame and Tkinter
class Colour:
    def __init__(self, r, g, b, a=255) -> None:
        self.tuple = (r, g, b, a)
        self.colour = pygame.Color(r, g, b, a)
        
        self.faded = pygame.Color(r, g, b, int(a * 0.392))
        # Creates a faded colour of the RGB values that is 39.2% more transparent

        self.hex = '#%02x%02x%02x' % (r, g, b)  
        # Creates a hex colour code from the RGB values      

    # In case colours need to be compared
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Colour):
            return __o.tuple == self.tuple
        return False


# Dictionary so colours can quickly be looked up using just a string
colours = {
    "black": Colour(0, 0, 0),
    "white": Colour(255, 255, 255),
    "grey": Colour(128, 128, 128),

    "red": Colour(255, 0, 0),
    "green": Colour(0, 255, 0),
    "blue": Colour(0, 0, 255),
    "dark green": Colour(56, 190, 70),
    "light blue": Colour(0, 157, 255),
    "cyan": Colour(0, 255, 255),
    "magenta": Colour(255, 0, 255),
    "yellow": Colour(255, 255, 0),
    "dark yellow": Colour(217, 179, 30),
    "orange": Colour(250, 126, 25),
    "purple": Colour(160, 32, 240),
    "violet": Colour(166, 66, 186),

    "transparent": Colour(0, 0, 0, 0),
    "faded black": Colour(0, 0, 0, 64),
    "faded white": Colour(255, 255, 255, 192)
}


# list of key values for graph colours
graphColours = [
    "red",
    "blue",
    "dark green",
    "dark yellow",
    "violet",
    "orange"
]


# get colour from graph index
def GetColourForPlotIndex(index):
    index = index % len(graphColours)
    return colours[graphColours[index]]

# get colour key from graph index
def GetColourKeyForPlotIndex(index):
    index = index % len(graphColours)
    return graphColours[index]