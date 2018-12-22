import sys
import time
import pygame


from cpu import *

KEY_MAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xc,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xd,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xe,
    pygame.K_z: 0xa,
    pygame.K_x: 0,
    pygame.K_c: 0xb,
    pygame.K_v: 0xf
}

class Emulator:
    def __init__(self, rom):
        self._running = False
        self.scaleFactor = 10
        self._display_surf = None
        self.font = None
        self.rom = rom
        self.debugWidth = 30
        self.cpu = CPU()
        self.background_color = (0, 0, 0)
        self.foreground_color = (255, 255, 255)
        self.size = self.width, self.height = 64 * self.scaleFactor, 32 * self.scaleFactor
        self.sizeWithDebug = self.size[0] + self.debugWidth * self.scaleFactor, self.size[1]

    def on_init(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("chip-8 emulator")
        pygame.mixer.music.load('beep.mp3')
        self.font = pygame.font.SysFont('Hack Regular', 2 * self.scaleFactor)
        self._display_surf = pygame.display.set_mode(self.sizeWithDebug, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill((255, 0, 0))
        self.cpu.load_rom(self.rom)
        self.cpu.start()
        self._running = True
        pygame.display.flip()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_MAP.keys():
                self.cpu.input[KEY_MAP[event.key]] = 1
        if event.type == pygame.KEYUP:
            if event.key in KEY_MAP.keys():
                self.cpu.input[KEY_MAP[event.key]] = 0

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
            self.cpu.control[0] = False
        # Check beep flag
        if self.cpu.control[1]:
            # beep
            pygame.mixer.music.play(0)
            self.cpu.control[1] = False
        self.update_debug_info()

    def clear_debug_info(self):
        debug_info = pygame.Surface((self.debugWidth * self.scaleFactor, self.height))
        debug_info.fill((0, 0, 0))
        self._display_surf.blit(debug_info, (self.width, 0))

    def update_debug_info(self):
        self.clear_debug_info()
        registers = self.font.render('registers', False, (255, 255, 255))
        for i in range(16):
            v = self.font.render("V%d: %X" % (i + 1, self.cpu.register[i]), False, (255, 255, 255))
            self._display_surf.blit(v, (self.width + 6 * self.scaleFactor * (i % 4), 2 * self.scaleFactor + 2 * self.scaleFactor * int(i / 4)))
        stack = self.font.render('stack', False, (255, 255, 255))
        stack_value = self.font.render(" ".join(str(x) for x in self.cpu.stack), False, (255, 255, 255))
        inputs = self.font.render('inputs', False, (255, 255, 255))
        for i in range(16):
            v = self.font.render("I%d: %s" % (i + 1, self.cpu.input[i]), False, (255, 255, 255))
            self._display_surf.blit(v, (self.width + 6 * self.scaleFactor * (i % 4), 15 + 14 * self.scaleFactor + 2 * self.scaleFactor * int(i / 4)))
        counters = self.font.render("I: %X   Delay: %X   Sound: %X   PC: %X" % (self.cpu .I, self.cpu.delayTimer, self.cpu.soundTimer, self.cpu.pc), False, (255, 255, 255))
        self._display_surf.blit(registers, (self.width, 0))
        self._display_surf.blit(stack, (self.width, 10 * self.scaleFactor))
        self._display_surf.blit(stack_value, (self.width, 10 * self.scaleFactor + 2 * self.scaleFactor))
        self._display_surf.blit(inputs, (self.width, 14 * self.scaleFactor))
        self._display_surf.blit(counters, (self.width, 24 * self.scaleFactor))

        pygame.display.flip()

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
    emulator = Emulator('roms/test.rom') #sys.argv[1]
    emulator.on_execute()
