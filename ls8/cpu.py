"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
RET = 0b00010001
CALL = 0b01010000
ADD = 0b10100000
SP = 7


# INTERRUPT IS A STRETCH GOAL
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.halted = False
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0

    def load(self):
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0
            # open the file (2nd arg)
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    instruction = t[0].strip()
                    # ignore the blank lines
                    if instruction == "":
                        continue

                    try:
                        instruction = int(instruction, 2)
                    except ValueError:
                        print(f"Invalid number '{instruction}")
                        sys.exit(1)

                    self.ram[address] = instruction
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
        elif op == MUL:
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
            instruction_to_execute = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            self.execute_instruction(instruction_to_execute, operand_a, operand_b)

    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.halted = True
            self.pc += 1

        elif instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 3

        elif instruction == PRN:
            print(self.reg[operand_a])
            self.pc += 2

        elif instruction == MUL:
            self.alu(instruction, operand_a, operand_b)
            self.pc += 3

        elif instruction == PUSH:
            # Decrement sp
            self.reg[SP] -= 1
            value_from_reg = self.reg[operand_a]
            self.ram_write(self.reg[SP], value_from_reg)
            self.pc += 2

        elif instruction == POP:
            topmost_value = self.ram_read(self.reg[SP])
            self.reg[operand_a] = topmost_value
            self.reg[SP] += 1
            self.pc += 2

        elif instruction == ADD:
            self.alu("ADD", operand_a, operand_b)
            self.pc += 3

        elif instruction == CALL:
            self.reg[SP] -= 1
            stack_address = self.reg[SP]
            returned_address = operand_b
            self.ram_write(stack_address, returned_address)
            register_number = self.ram_read(operand_a)
            self.pc = self.reg[register_number]

        elif instruction == RET:
            self.pc = self.ram_read(self.reg[SP])
            self.reg[SP] += 1

        else:
            print("Unknown Operation..")
            sys.exit(1)
