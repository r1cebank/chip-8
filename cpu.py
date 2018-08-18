import logging
from clock import *
from random import randint

logging.basicConfig(level=logging.DEBUG)


class CPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.register = [0] * 16
        self.I = 0
        self.frameBuffer = [0] * 32 * 64
        self.stack = []
        self.input = [0] * 16
        self.instruction = 0

        # Timers
        self.delayTimer = 0
        self.soundTimer = 0
        self.flush = False

        # Clock
        self.speed = 1 # Hz
        self.clock = None

        # Counters
        self.pc = 0x200

        self.funcmap = {
            0x0000: self._0000,
            0x00e0: self._00e0,
            0xc000: self._C000,
            0xa000: self._A000
        }

        logging.debug("CPU initialized.")

    def _0000(self):
        extracted_op = self.instruction & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))

    def _00e0(self):
        # 00E0 - CLS
        # Clear the display.
        logging.info('Clearing Screen')

    def _A000(self):
        # Annn - LD I, addr
        # Set I = nnn.
        # The value of register I is set to nnn.
        logging.info("Sets I to the address NNN.")
        self.I = self.instruction & 0x0fff

    def _C000(self):
        # Cxkk - RND Vx, byte
        # Set Vx = random AND kk.
        logging.info('Generate Random Number')
        self.register[self.vx] = randint(0, 255) & (self.instruction & 0x00ff)

    def load_rom(self, rom):
        logging.debug("Loading %s..." % rom)
        romdata = open(rom, 'rb').read()
        for index, val in enumerate(romdata):
            self.memory[0x200 + index] = val
        logging.debug("ROM Loaded")

    def start(self):
        self.clock = clock(1 / self.speed, self.cycle)

    def stop(self):
        if self.clock is not None:
            self.clock.cancel()

    def cycle(self):
        self.instruction = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        #
        # TODO: process this opcode here
        #
        self.vx = (self.instruction & 0x0f00) >> 8
        self.vy = (self.instruction & 0x00f0) >> 4
        self.pc += 2

        # 2. check ops, lookup and execute
        extracted_op = self.instruction & 0xf000
        try:
            self.funcmap[extracted_op]()  # call the associated method
        except:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))


        # decrement timers
        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                pass
