import logging

logging.basicConfig(level=logging.DEBUG)

class CPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.register = [0] * 16
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

        self.funcmap = {
            0x0000: self._0000
        }

        logging.debug("CPU initialized.")

    def _0000(self):
        extracted_op = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            logging.warn("Unknown instruction: %X" % self.opcode)

    def load_rom(self, rom):
        logging.debug("Loading %s..." % rom)
        romdata = open(rom, 'rb').read()
        for index, val in enumerate(romdata):
            self.memory[0x200 + index] = val
        logging.debug("ROM Loaded")

    def cycle(self):
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        #
        # TODO: process this opcode here
        #
        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4
        self.pc += 2

        # 2. check ops, lookup and execute
        extracted_op = self.opcode & 0xf000
        try:
            self.funcmap[extracted_op]()  # call the associated method
        except:
            logging.warn("Unknown instruction: %X" % self.opcode)


        # decrement timers
        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                pass
