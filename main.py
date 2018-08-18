import sys
import time
import pygame

from cpu import *

class Emulator:
    def __init__(self, rom):
        self._running = True
        self.scaleFactor = 10
        self._display_surf = None
        self.rom = rom
        self.cpu = CPU()
        self.size = self.weight, self.height = 64 * self.scaleFactor, 32 * self.scaleFactor

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("chip-8 emulator")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.cpu.load_rom(self.rom)
        self.cpu.start()
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
        self.cpu.stop()

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
    emulator = Emulator('roms/rand.rom') #sys.argv[1]
    emulator.on_execute()
