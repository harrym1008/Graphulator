import main, colours, pygame

offset = 0, 0
zoom = 10

bounds = []


def DrawAxis():
    # create the surface for the axis to be drawn on
    axisSurface = pygame.Surface(main.screensize)

    drawCentre = 0 - offset[0], 0 - offset[1]
    rect = pygame.draw.line(drawCentre, pygame.Color)

