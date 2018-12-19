import logging
from clock import *
from random import randint

logging.basicConfig(level=logging.DEBUG)


class CPU:
    memory = [0] * 4096
    register = [0] * 16
    I = 0
    frameBuffer = [0] * 64 * 32
    stack = []
    input = [0] * 16
    instruction = 0

    # Timers
    delayTimer = 0
    soundTimer = 0
    flush = False

    # Clock
    speed = 50  # Hz
    clock = None

    # Counters
    pc = 0x200

    # Font
    font = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80   # F
    ]

    # Control lines
    # 0 - flush display
    # 1 - beep
    control = [0] * 16

    def __init__(self):

        self.funcmap = {
            0x0000: self._0000,
            0x00e0: self._00e0,
            0x3000: self._3000,
            0x4000: self._4000,
            0x8000: self._8000,
            0x8ff0: self._8FF0,
            0x8ff1: self._8FF1,
            0x8ff2: self._8FF2,
            0x8ff3: self._8FF3,
            0x8ff4: self._8FF4,
            0x8ff5: self._8FF5,
            0x8ff6: self._8FF6,
            0x8ff7: self._8FF7,
            0x8ffe: self._8FFE,
            0xc000: self._C000,
            0xa000: self._A000,
            0xf000: self._F000,
            0xf01e: self._F01E,
            0xe000: self._E000,
            0xe0a1: self._E0A1,
            0xf033: self._F033,
            0xf065: self._F065,
            0xf029: self._F029,
            0xf055: self._F055,
            0x6000: self._6000,
            0x5000: self._5000,
            0xd000: self._D000,
            0xf00a: self._F00A,
            0x1000: self._1000,
            0x2000: self._2000,
            0x7000: self._7000,
            0x00ee: self._00ee,
            0xf015: self._F015,
            0xf007: self._F007,
            0xf018: self._F018
        }

        # Loading font in memory
        for i in range(len(self.font)):
            # load 80-char font set
            self.memory[i] = self.font[i]

        logging.debug("CPU initialized.")

    def _0000(self):
        extracted_op = self.instruction & 0xf0ff
        if extracted_op in self.funcmap:
            try:
                self.funcmap[extracted_op]()
            except:
                logging.error("Instruction error: %X, op: %X" % (self.instruction, extracted_op))
        else:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))
            self.stop();

    def _1000(self):
        # 1nnn - JMP
        # Jump to location nnn.
        logging.info("Jumping to %X", self.instruction % 0x0fff)
        self.pc = self.instruction & 0x0fff

    def _2000(self):
        # 2nnn
        # Call a subroutine at nnn
        logging.info('Calling subroutine at %X', self.instruction & 0x0fff)
        self.stack.append(self.pc)
        self.pc = self.instruction & 0x0fff

    def _3000(self):
        # Skip next instruction if Vx = kk.
        logging.info('Skip next instruction if Vx = kk.')
        if self.register[self.vx] == (self.instruction & 0x00ff):
            self.pc += 2

    def _4000(self):
        # Skip next instruction if Vx != kk.
        logging.info("Skip next instruction if Vx != kk.")
        if self.register[self.vx] != (self.instruction & 0x00ff):
            self.pc += 2

    def _5000(self):
        # skip next instruction if Vx = Vy
        logging.info("Skip next instruction if Vx = Vy.")
        if self.register[self.vx] == self.register[self.vy]:
            self.pc += 2

    def _7000(self):
        # 7xkk
        # Set Vx = Vx + kk.
        logging.info('Adding %X to VX', self.instruction & 0xff)
        self.register[self.vx] += (self.instruction & 0xff)

    def _8000(self):
        extracted_op = self.instruction & 0xf00f
        extracted_op += 0xff0
        if extracted_op in self.funcmap:
            try:
                self.funcmap[extracted_op]()
            except:
                logging.error("Instruction error: %X, op: %X" % (self.instruction, extracted_op))
        else:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))
            self.stop();

    def _8FF0(self):
        # Set Vx = Vy.
        logging.info("Set Vx = Vy.")
        self.register[self.vx] = self.register[self.vy]
        self.register[self.vx] &= 0xff

    def _8FF1(self):
        # Set Vx = Vx OR Vy.
        logging.info("Set Vx = Vx OR Vy.")
        self.register[self.vx] |= self.register[self.vy]
        self.register[self.vx] &= 0xff

    def _8FF2(self):
        # Set Vx = Vx AND Vy.
        logging.info("Set Vx = Vx AND Vy.")
        self.register[self.vx] &= self.register[self.vy]
        self.register[self.vx] &= 0xff
    
    def _8FF3(self):
        # Set Vx = Vx XOR Vy.
        logging.info("Set Vx = Vx XOR Vy.")
        self.register[self.vx] ^= self.register[self.vy]
        self.register[self.vx] &= 0xff

    def _8FF4(self):
        # Set Vx = Vx + Vy, set VF = carry.
        logging.info("Set Vx = Vx + Vy, set VF = carry.")
        if self.register[self.vx] + self.register[self.vy] > 0xff:
            self.register[0xf] = 1
        else:
            self.register[0xf] = 0
        self.register[self.vx] += self.register[self.vy]
        self.register[self.vx] &= 0xff

    def _8FF5(self):
        # Set Vx = Vx - Vy, set VF = NOT borrow.
        logging.info("Set Vx = Vx - Vy, set VF = NOT borrow.")
        if self.register[self.vy] > self.register[self.vx]:
            self.register[0xf] = 0
        else:
            self.register[0xf] = 1
        self.register[self.vx] = self.register[self.vx] - self.register[self.vy]
        self.register[self.vx] &= 0xff

    def _8FF6(self):
        # Set Vx = Vx SHR 1.
        logging.info("Set Vx = Vx SHR 1.")
        self.register[0xf] = self.register[self.vx] & 0x0001
        self.register[self.vx] = self.register[self.vx] >> 1

    def _8FF7(self):
        # Set Vx = Vy - Vx, set VF = NOT borrow.
        logging.info("Set Vx = Vy - Vx, set VF = NOT borrow.")
        if self.register[self.vx] > self.register[self.vy]:
            self.register[0xf] = 0
        else:
            self.register[0xf] = 1
        self.register[self.vx] = self.register[self.vy] - self.register[self.vx]
        self.register[self.vx] &= 0xff

    def _8FFE(self):
        # Set Vx = Vx SHL 1.
        logging.info("Set Vx = Vx SHL 1.")
        self.register[0xf] = (self.register[self.vx] & 0x00f0) >> 7
        self.register[self.vx] = self.register[self.vx] << 1
        self.register[self.vx] &= 0xff

    def _00e0(self):
        # 00E0 - CLS
        # Clear the display.
        logging.info('Clearing Screen')
        self.frameBuffer = [0] * 64 * 32
        self.control[0] = True

    def _00ee(self):
        # RET
        # Return from a subroutine.
        logging.info('Return from subroutine')
        self.pc = self.stack.pop()

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

    def _E000(self):
        extracted_op = self.instruction & 0xf0ff
        if extracted_op in self.funcmap:
            try:
                self.funcmap[extracted_op]()
            except:
                logging.error("Instruction error: %X, op: %X" % (self.instruction, extracted_op))
        else:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))
            self.stop();

    def _E0A1(self):
        # ExA1 SKNP Vx
        # Skip next instruction if key with the value of Vx is not pressed.
        logging.info("Skip next instruction if key with the value of Vx is not pressed.")
        if self.input[self.vx] == 0:
            self.pc += 2

    def _F000(self):
        extracted_op = self.instruction & 0xf0ff
        if extracted_op in self.funcmap:
            try:
                self.funcmap[extracted_op]()
            except:
                logging.error("Instruction error: %X, op: %X" % (self.instruction, extracted_op))
        else:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))
            self.stop();

    def _F007(self):
        # Set Vx = delay timer value.
        logging.info('Set Vx = delay timer')
        self.register[self.vx] = self.delayTimer

    def _F015(self):
        # Set delay timer = Vx.
        logging.info('Set delay timer = Vx')
        self.delayTimer = self.register[self.vx]

    def _F018(self):
        # Set sound timer = Vx.
        logging.info("Set sound timer = Vx.")
        self.soundTimer = self.register[self.vx]
    
    def _F01E(self):
        # Set I = I + Vx.
        logging.info("Set I = I + Vx.")
        self.I += self.register[self.vx]
        if self.I > 0xfff:
            self.register[0xf] = 1
            self.I &= 0xfff
        else:
            self.register[0xf] = 0

    def _F033(self):
        # Store BCD representation of Vx in memory locations I, I+1, and I+2.
        logging.info("Storing BCD to Memory")
        self.memory[self.I] = int(self.register[self.vx] / 100)
        self.memory[self.I + 1] = int((self.register[self.vx] % 100) / 10)
        self.memory[self.I + 2] = int(self.register[self.vx] % 10)

    def _F055(self):
        # Store registers V0 through Vx in memory starting at location I.
        logging.info("Store registers V0 through Vx in memory starting at location I.")
        i = 0
        while i <= self.vx:
            self.memory[self.I + i] = self.register[i]
            i += 1
        self.I += (self.vx) + 1

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
        self.register[0xf] = 0
        x = self.register[self.vx] & 0xff
        y = self.register[self.vy] & 0xff

        height = self.instruction & 0x000f
        row = 0
        while row < height:
            curr_row = self.memory[row + self.I]
            pixel_offset = 0
            while pixel_offset < 8:
                loc = x + pixel_offset + ((y + row) * 64)
                pixel_offset += 1
                if (y + row) >= 32 or (x + pixel_offset - 1) >= 64:
                    # ignore pixels outside the screen
                    continue
                mask = 1 << 8 - pixel_offset
                curr_pixel = (curr_row & mask) >> (8 - pixel_offset)
                self.frameBuffer[loc] ^= curr_pixel
                if self.frameBuffer[loc] == 0:
                    self.register[0xf] = 1
                else:
                    self.register[0xf] = 0
            row += 1
        self.control[0] = True


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
        logging.debug('Resetting CPU')
        logging.debug("Loading %s..." % rom)
        romdata = open(rom, 'rb').read()
        for index, val in enumerate(romdata):
            self.memory[0x200 + index] = val
        logging.debug("ROM Loaded")

    def reset(self):
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

        # Counters
        self.pc = 0x200

        # Control lines
        # 0 - flush display
        self.control = [0] * 16

        logging.debug("CPU is reset.")

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
        if extracted_op in self.funcmap:
            try:
                self.funcmap[extracted_op]()
            except:
                logging.error("Instruction error: %X, op: %X" % (self.instruction, extracted_op))
        else:
            logging.warn("Unknown instruction: %X, op: %X" % (self.instruction, extracted_op))
            self.stop();


        # decrement timers
        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                self.control[1] = True
