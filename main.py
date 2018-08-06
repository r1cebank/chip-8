import pygame

from cpu import *

class Emulator:
    def __init__(self):
        self._running = True
        self.scaleFactor = 10
        self._display_surf = None
        self.cpu = CPU()
        self.size = self.weight, self.height = 64 * self.scaleFactor, 32 * self.scaleFactor

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("chip-8 emulator")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        pass

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    emulator = Emulator()
    emulator.on_execute()
