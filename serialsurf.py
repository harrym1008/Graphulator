import pygame
import numpy as np
import time



# This is a class that converts a pygame Surface into a serialisable
# Numpy array that can be transferred in queues

class SerialisedSurface:
    def __init__(self, surface):
        self.rgbChannels = pygame.surfarray.array3d(surface)
        self.alphaChannel = pygame.surfarray.array_alpha(surface)

        self.npArray = SerialisedSurface.CombineRGBAndAlpha(self.rgbChannels, self.alphaChannel)


    def GetSurface(self):
        return SerialisedSurface.MakeSurfaceRGBA(self.npArray)


    @classmethod
    def CombineRGBAndAlpha(cls, rgb, alpha):        
        return np.dstack((rgb, alpha))
        

    # https://github.com/pygame/pygame/issues/1244
    @classmethod
    def MakeSurfaceRGBA(cls,  array):
        shape = array.shape

        if shape[2] == 3:
            return pygame.surfarray.make_surface(array)
        elif len(shape) != 3 and shape[2] != 4:
            raise ValueError("Array is not RGBA: (x, y, 4)")
        
        surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)
        pygame.pixelcopy.array_to_surface(surface, array[:,:,0:3])

        surfaceAlpha = np.array(surface.get_view("A"), copy=False)
        surfaceAlpha[:,:] = array[:,:,3]

        return surface