import logging

logging.basicConfig(level=logging.DEBUG)

class CPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.io = [0] * 16
        self.frameBuffer = [0] * 32 * 64
        self.stack = []
        self.input = [0] * 16
        self.opcode = 0

        # Timers
        self.delayTimer = 0
        self.soundTimer = 0
        self.flush = False

        # Counters
        self.pc = 0x200

        logging.debug("CPU initialized.")

    def load_rom(self, rom):
        logging.debug("Loading %s..." % rom)
        binary = open(rom, "rb").read()
        i = 0
        while i < len(binary):
            self.memory[i + 0x200] = ord(binary[i])
            i += 1

    def cycle(self):
        self.opcode = self.memory[self.pc]

        #
        # TODO: process this opcode here
        #

        # After
        self.pc += 2

        # decrement timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                pass