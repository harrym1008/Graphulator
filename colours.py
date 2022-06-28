import pygame

colours = {
    "black": (0, 0, 0),
    "white": (250, 255, 255),

    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0)
}

TRANSPARENT = pygame.Color(0, 0, 0, 0)


hexLetters = "0123456789abcdef"


def PygameColour(key: str) -> pygame.Color:
    colourTuple = colours[key]
    return pygame.Color(colourTuple[0], colourTuple[1], colourTuple[2])


def HexColour(key: str) -> str:
    r, g, b = colours[key]
    hexValues = [r // 16, r % 16, g // 16, g % 16, b // 16, b % 16]

    hexStr = ""
    for val in hexValues:
        hexStr += hexLetters[val]

    return hexStr
