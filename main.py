import sys
import time
import pygame


from cpu import *

class Emulator:
    def __init__(self, rom):
        self._running = False
        self.scaleFactor = 10
        self._display_surf = None
        self.rom = rom
        self.cpu = CPU()
        self.background_color = (0, 255, 0)
        self.foreground_color = (255, 255, 255)
        self.size = self.width, self.height = 64 * self.scaleFactor, 32 * self.scaleFactor

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("chip-8 emulator")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill((255, 0, 0))
        self.cpu.load_rom(self.rom)
        self.cpu.start()
        self._running = True
        pygame.display.flip()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        # Copy the framebuffer to screen
        background = pygame.Surface((64, 32))
        for i in range(len(self.cpu.frameBuffer)):
            if self.cpu.frameBuffer[i]:
                background.set_at((i % 64, int(i / 64)), self.foreground_color)
            else:
                background.set_at((i % 64, int(i / 64)), self.background_color)
        background = pygame.transform.scale(background, self.size)
        background = background.convert()
        self._display_surf.blit(background, (0, 0))
        # Check flush flag
        if self.cpu.control[0]:
            self.on_render()

    def on_render(self):
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
        self.cpu.stop()

    def on_execute(self):
        if not self._running:
            self.on_init()
            self._running = True

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
        self.on_cleanup()


if __name__ == "__main__":
    emulator = Emulator('roms/rand.rom') #sys.argv[1]
    emulator.on_execute()
