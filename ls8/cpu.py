"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.flag = 0b00000000

    def ram_read(self, MAR):
        print(f"READING... {self.ram[MAR]}")
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        os.chdir('./examples')

        program = []

        with open(sys.argv[1]) as f:
            for i in f:
                if(i[0] == '0' or i[0] == '1'):
                    step = int(i[0:8], 2)
                    program.append(step)
                    
        for instruction in program:
            self.ram[address] = instruction
            address += 1

        print(program)
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "SQRT":
            self.reg[reg_a] ** 0.5
        elif op == "POW":
            self.reg[reg_a] **= self.reg[reg_b]
        elif op == "CMP":
            # `FL` bits: `00000LGE`
            if(self.reg[reg_a] < self.reg[reg_b]):
                self.flag = 0b00000100
            else:
                self.flag = 0b00000000
            if(self.reg[reg_a] > self.reg[reg_b]):
                self.flag = 0b00000010
            else:
                self.flag = 0b00000000
            if(self.reg[reg_a] == self.reg[reg_b]):
                self.flag = 0b00000001
            else:
                self.flag = 0b00000000
            
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        IR = self.ram[self.pc]
        HALT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        PUSH = 0b01000101
        POP = 0b01000110
        MUL = 0b10100010
        SP = 7
        self.reg[SP] = 0xF4
        FL = 0b00000011
        FL |= 0b00000001
        
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110
        print(f'FL: {bin(FL)}')
        def push_val(value):
            self.reg[SP] -= 1
            top_of_stack_addr = self.reg[SP]
            self.ram_write(top_of_stack_addr, value)

        def pop_val():
            top_of_stack_addr = self.reg[SP]
            value = self.ram[top_of_stack_addr]
            self.reg[SP] += 1
            return value

        while(IR != HALT):
            # self.trace()
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            IR = self.ram[self.pc]
            
            if(IR == LDI):
                address = operand_a
                
                value = operand_b
                print(f"In Write to Reg with address {address}, and value {value}")
                
                self.reg[address] = value
                print(f'REG: {self.reg}')
                self.pc += 3
                
            elif(IR == PRN):
                address = self.ram[self.pc + 1]
                print(f'READING... {self.reg[address]}')
                self.pc += (IR//64) + 1
            elif(IR == MUL):
                ope = "MUL"
                val1 = operand_a
                
                val2 = operand_b

                self.alu(ope, val1, val2)
                self.pc += (IR//64) + 1

            elif(IR == ADD):
                ope = "ADD"
                val1 = operand_a
                val2 = operand_b
                self.alu(ope, val1, val2)
                self.pc += (IR//64) + 1

            elif(IR == CMP):
                ope = "CMP"
                val1 = operand_a
                val2 = operand_b
                self.alu(ope, val1, val2)
                self.pc += (IR//64) + 1

            elif(IR == PUSH):
                self.reg[SP] -= 1

                reg_num = self.ram[self.pc + 1]
                value = self.reg[reg_num]

                top_of_stack_addr = self.reg[SP]
                self.ram_write(top_of_stack_addr, value)

                self.pc += (IR//64) + 1

                print(f'PUSH: {self.ram[0xf0:0xf4]}')

            elif(IR == POP):

                top_of_stack_addr = self.reg[SP]
                value = self.ram[top_of_stack_addr]

                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value

                self.reg[SP] += 1
                
                self.pc += (IR//64) + 1

                print(f'POP: {self.ram[0xf0:0xf4]}')

            elif(IR == CALL):
                return_addr = self.pc + (IR//64) + 1
                push_val(return_addr)
                reg_num = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr


            elif(IR == RET):
                return_addr = pop_val()
                self.pc = return_addr

            elif(IR == JMP):
                
                # Jump to the address stored in the given register.
                addr = self.reg[operand_a]
                # Set the `PC` to the address stored in the given register.
                self.pc = addr
                '''
                Machine code:
                ```
                01010100 00000rrr
                54 0r
                ```
                '''
            elif(IR == JEQ):
                if(self.flag == 0b00000001):
                    addr = self.reg[operand_a]
                    self.pc = addr
                else:
                    self.pc += (IR//64) + 1

            elif(IR == JNE):
                if(self.flag == 0b00000000):
                    addr = self.reg[operand_a]
                    self.pc = addr
                else:
                    self.pc += (IR//64) + 1

            elif(IR == HALT):
                break
            else:
                print(f"Error, the instruction {IR} at address {self.pc} is not recognized")
                sys.exit()

