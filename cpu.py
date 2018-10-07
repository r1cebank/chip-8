import logging
from clock import *
from random import randint

logging.basicConfig(level=logging.DEBUG)


class CPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.register = [0] * 16
        self.I = 0
        self.frameBuffer = [0] * 64 * 32
        self.stack = []
        self.input = [0] * 16
        self.instruction = 0

        # Timers
        self.delayTimer = 0
        self.soundTimer = 0
        self.flush = False

        # Clock
        self.speed = 5 # Hz
        self.clock = None

        # Counters
        self.pc = 0x200

        self.funcmap = {
            0x0000: self._0000,
            0x00e0: self._00e0,
            0xc000: self._C000,
            0xa000: self._A000,
            0xf000: self._F000,
            0xf033: self._F033,
            0xf065: self._F065,
            0xf029: self._F029,
            0x6000: self._6000,
            0xd000: self._D000,
            0xf00a: self._F00A,
            0x1000: self._1000
        }

        # Control lines
        # 0 - flush display
        self.control = [0] * 16

        logging.debug("CPU initialized.")

    def _0000(self):
        extracted_op = self.instruction & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))

    def _1000(self):
        # 1nnn - JMP
        # Jump to location nnn.
        logging.info("Jumping to %X", self.instruction % 0x0fff)
        self.pc = self.instruction & 0x0fff

    def _00e0(self):
        # 00E0 - CLS
        # Clear the display.
        self.frameBuffer = [0] * 32 * 64
        self.control[0] = True
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

    def _F000(self):
        extracted_op = self.instruction & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except Exception as e:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))

    def _F033(self):
        # Store BCD representation of Vx in memory locations I, I+1, and I+2.
        logging.info('Storing BCD to Memory')
        self.memory[self.I] = int(self.register[self.vx] / 100)
        self.memory[self.I + 1] = int((self.register[self.vx] % 100) / 10)
        self.memory[self.I + 2] = int(self.register[self.vx] % 10)

    def _F065(self):
        # Read registers V0 through Vx from memory starting at location I.
        logging.info("Fills V0 to VX with values from memory starting at address I.")
        i = 0
        while i <= self.vx:
            self.register[i] = self.memory[self.I + i]
            i += 1
        self.I += self.vx + 1

    def _F029(self):
        # Set I = location of sprite for digit Vx.
        logging.info('Set index to point to location of vx')
        try:
            self.I = (5 * (self.register[self.vx])) & 0xfff
        except Exception as e:
            logging.error(e)

    def _6000(self):
        # Set Vx = kk.
        logging.info('Set vx to kk')
        self.register[self.vx] = self.instruction & 0x00ff

    def _D000(self):
        # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        logging.info('Display sprite at I')


    def _F00A(self):
        # Wait for a key press, store the value of the key in Vx.
        logging.info('Wait for keypress')
        key = -1
        for i in range(len(self.input)):
            if self.input[i] == 1:
                key = i
        if key >= 0:
            self.input[self.vx] = key
        else:
            self.pc -= 2

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
        except Exception as e:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))


        # decrement timers
        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                pass
