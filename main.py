import tkinter as tk
import pygame, threading, time, sys, os
import tkinter.font as font

running = True


def PygameLoop():
    global running, graphScreen

    clock = pygame.time.Clock()

    while running:
        clock.tick(60)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                Kill()
                break
            if e.type == pygame.VIDEORESIZE:
                pass
                # if e.w > 64 and e.h > 64:
                #     graphScreen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)


def BeforeThreads():
    guiScreen




def Main():
    pass


def Kill():
    global running
    running = False
    pygame.display.quit()
    guiScreen.destroy()
    quit()


if __name__ == "__main__":
    guiScreen = tk.Tk()
    guiScreen.title("Graphulator v2")

    pygame.init()
    graphScreen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Display Window")

    # pygame loop thread
    pygameThread = threading.Thread(target=PygameLoop)
    pygameThread.start()

    # creating a thread for the main screen
    thread = threading.Thread(target=Main)
    thread.start()

    # run Kill() when the tkinter window is closed
    guiScreen.protocol("WM_DELETE_WINDOW", Kill)
    # using the main thread to do tkinter (required by the Tkinter module)
    guiScreen.mainloop()
