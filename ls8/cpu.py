"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

"""
PC: Program Counter, address of the currently executing instruction
IR: Instruction Register, contains a copy of the currently executing instruction
MAR: Memory Address Register, holds the memory address we're reading or writing
MDR: Memory Data Register, holds the value to write or the value just read
FL: Flags, see below
"""


# INTERRUPT IS A STRETCH GOAL
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.halted = False
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4  # This is reserved for the stack pointer
        self.pc = 0
        self.fl = 0

    def load(self, filename):
        """Load a program into memory."""

        address = 0
        try:
            with open(filename) as fp:
                for line in fp:
                    line = line.strip()
                    if line == "" or line[0] == "#":
                        continue
                    try:
                        str_value = line.split("#")[0]
                        value = int(str_value, 10)
                    except ValueError:
                        print(f"Invalid Number: {str_value}")
                        sys.exit(1)
                    self.ram_write(address)
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.halted:
            instruction_to_execute = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction_to_execute, operand_a, operand_b)
        else:
            print("Unknown instruction {instruction} at address {pc}")
            sys.exit(1)

    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.halted = True
            self.pc += 1
        elif instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 3
        elif instruction == PRN:
            val = self.reg[operand_a]
            print(val)
            self.pc += 2