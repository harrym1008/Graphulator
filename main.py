import tkinter as tk
import pygame, threading
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
    global guiScreen
    title = tk.Label(guiScreen, text="Graphulator   ")
    title.config(font=("Arial", 20, "bold"))
    title.grid(row=0, column=0, columnspan=3)
    author = tk.Label(guiScreen, text="A graphing calculator made by Harrison McGrath", justify=tk.LEFT)
    author.config(font=("Arial", 8))
    author.grid(row=1, column=0, columnspan=3)

    equations = []

    EQUATIONS_AMOUNT = 10
    EQUATIONS_OFFSET = 2

    for row in range(EQUATIONS_AMOUNT):
        txt = tk.Label(guiScreen, text=f"   Equation {row + 1}")
        txt.config(font=("Arial", 12))
        txt.grid(row=row+EQUATIONS_OFFSET, column=0)
        txt = tk.Label(guiScreen, text=f"   y =")
        txt.config(font=("Arial", 12, "bold"))
        txt.grid(row=row+EQUATIONS_OFFSET, column=1)
        equations.append(tk.Entry(master=guiScreen))
        equations[row].grid(row=row+EQUATIONS_OFFSET, column=2)




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

    BeforeThreads()

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
