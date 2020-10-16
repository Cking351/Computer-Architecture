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
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
JLT = 0b01011000
JGT = 0b01010111
JGE = 0b01011000
SP = 7


# INTERRUPT IS A STRETCH GOAL
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.halted = False
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.fl = 0b00000000  # Set flag to zero

    def load(self):
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    instruction = t[0].strip()
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
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                # Raise "L" flag to "1"
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # Raise "G" flag to "1"
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                # Raise "E" flag to "1"
                self.fl = 0b00000001
            else:
                self.fl = 0b00000000
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

    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.halted = True
            self.pc += 1
            sys.exit(1)

        elif instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 3

        elif instruction == PRN:
            print(self.reg[operand_a])
            self.pc += 2

        elif instruction == MUL:
            self.alu("MUL", operand_a, operand_b)
            self.pc += 3

        elif instruction == PUSH:
            # Decrement sp
            self.reg[SP] -= 1
            value_from_reg = self.ram_read(self.pc + 1)
            self.ram[self.reg[SP]] = value_from_reg
            self.pc += 2

        elif instruction == POP:
            address_to_pop = self.reg[SP]
            value = self.ram[address_to_pop]
            reg_num = self.ram[self.pc + 1]
            self.reg[reg_num] = value
            self.reg[SP] += 1
            self.pc += 2

        elif instruction == ADD:
            self.alu("ADD", operand_a, operand_b)
            self.pc += 3

        elif instruction == CALL:
            self.pc += 1
            self.reg[SP] -= 1
            self.ram[self.reg[SP]] = self.pc + 1
            self.pc = self.reg[self.ram_read(self.pc)]

        elif instruction == RET:
            next_address = self.ram_read(self.reg[SP])
            self.reg[SP] += 1
            self.pc = next_address

        elif instruction == CMP:  # Set Flags in ALU
            self.alu("CMP", operand_a, operand_b)
            self.pc += 3

        elif instruction == JMP:  # Jump to given address
            self.pc = self.reg[operand_a]

        elif instruction == JEQ:  # Check if Equal flag is true using logical AND
            equal = self.fl & 0b00000001  # 1?
            if equal:
                self.pc = self.reg[operand_a]  # Jump to address in given reg
            else:
                self.pc += 2

        elif instruction == JNE:  # Check if Equal flag is clear (0) move to address in given reg
            equal = self.fl & 0b00000001
            if not equal:
                self.pc = self.reg[operand_a]
            else:
                self.pc += 2

        else:
            print("Unknown Operation..", instruction)
            sys.exit(1)
