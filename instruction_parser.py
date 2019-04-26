class instruction_parser(object):
    def __init__(self, content):
        # Below is the register file to be populated, init to all zeros
        self.register_file = dict([("R%s" % x, 0) for x in range(32)])

        # Below is the memory to be populated, 0, 4, ... 996, init to all zeros
        self.memory = dict([(x * 4, 0) for x in range(1000 / 4)])

        # The following 8 instructions are supported
        # 2 data transfers:     LW, SW
        # 4 arithmetic/logic:   ADD, ADDI, SUB, SLT
        # 2 control flow:       BEQ, BNE

        # Divide content into registers, memory, and code lists
        self.reg_values = (content[content.index('REGISTERS') + 1 : content.index('MEMORY')])
        self.mem_values = (content[content.index('MEMORY') + 1 : content.index('CODE')])
        self.code_lines = (content[content.index('CODE') + 1 : ])

        # remove empty strings from lists
        self.reg_values = filter(None, self.reg_values)
        self.mem_values = filter(None, self.mem_values)
        self.code_lines = filter(None, self.code_lines)

        # Below is the final instruction list to be populated, init to None
        self.final_instruction = dict([("I%s" % x, None) for x in range(len(self.code_lines))])

        # PARSE THE REG FILE
        self.parse_reg_file()

        # PARSE THE MEMORY
        self.parse_memory()

        # PARSE THE CODE
        # NOTE: each instruction is parsed separately solely for reader clarity
        for i in xrange(len(self.code_lines)):
            # Check if R-type instruction, otherwise it must be I-type
            if self.code_lines[i][0:6] == '000000':
                self.parse_r_type(self.code_lines[i][:], i)
            else:
                self.parse_i_type(self.code_lines[i][:], i)


    def parse_reg_file(self):
        # Add the register value to the corresponding register file dictionary)
        for i in xrange(len(self.reg_values)):
            temp = self.reg_values[i][:].split()
            for j in range(32):
                if temp[0] == ('R%d' % j):
                    self.register_file['R%d' % j] = int(temp[1])


    def parse_memory(self):
        # Add the memory value to the corresponding memory dictionary
        for i in xrange(len(self.mem_values)):
            temp = self.mem_values[i][:].split()
            for j in range(1000 / 4):
                j *= 4
                if temp[0] == ('%d' % j):
                    self.memory[j] = int(temp[1])


    def parse_r_type(self, code_line, index):
        # Set control lines, same set for all R-format instructions
        # EX stage control lines
        alu_op      = '10'  # ALUOp1 = 1 and ALUOp0 = 0
        reg_read    = 1  # Always true, always reading from register
        # MEM stage control lines
        mem_read    = 0     # none (0), read data from memory address (1)
        mem_write   = 0     # none (0), write data to memory address (1)
        # WB stage control lines
        reg_write   = 1     # none (0) OR write corresponding data to the register file (1)
        mem_to_reg  = 0     # write ALU data (0) OR memory data (1)

        # Get 6 lowest bits (5 - 0), this is the func code
        lowest_six_bits = code_line[26:32].strip()

        # op code is same for all R-type instructions
        op = 0
        # Check if SLT instruction, rd := (rs < rt)
        if lowest_six_bits == '101010':
            rs = int(code_line[6:11].strip(), 2)
            rt = int(code_line[11:16].strip(), 2)
            rd = int(code_line[16:21].strip(), 2)
            shamt = 0
            func = 42
            self.final_instruction['I%s' % index] = dict([('inst', 'SLT'),('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('rd', rd),
                                                     ('shamt', shamt),
                                                     ('func', func),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write),
                                                     ('mem_to_reg', mem_to_reg)])

        # Check if ADD instruction, rd := (rs + rt)
        elif lowest_six_bits == '100000':
            rs = int(code_line[6:11].strip(), 2)
            rt = int(code_line[11:16].strip(), 2)
            rd = int(code_line[16:21].strip(), 2)
            shamt = 0
            func = 32
            self.final_instruction['I%s' % index] = dict([('inst', 'ADD'),('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('rd', rd),
                                                     ('shamt', shamt),
                                                     ('func', func),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write),
                                                     ('mem_to_reg', mem_to_reg)])
        # Check if SUB instruction, rd := (rs - rt)
        elif lowest_six_bits == '100010':
            rs = int(code_line[6:11].strip(), 2)
            rt = int(code_line[11:16].strip(), 2)
            rd = int(code_line[16:21].strip(), 2)
            shamt = 0
            func = 34
            self.final_instruction['I%s' % index] = dict([('inst', 'SUB'),('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('rd', rd),
                                                     ('shamt', shamt),
                                                     ('func', func),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write),
                                                     ('mem_to_reg', mem_to_reg)])
        else:
            print 'ERROR: Unable to parse: ', code_line
            return 'EXIT'


    def parse_i_type(self, code_line, index):
        # Get 6 highest bits (31 - 26)
        highest_six_bits = code_line[0:6].strip()

        # Check if LW instruction, rt := memory[rs + immed]
        if highest_six_bits == '100011':
            # Set control lines for LW
            # EX stage control lines
            alu_op      = '00'  # ALUOp1 = 0 and ALUOp0 = 0
            reg_read    = 1     # Always true, always reading from register
            # MEM stage control lines
            mem_read    = 1     # none (0), read data from memory address (1)
            mem_write   = 0     # none (0), write data to memory address (1)
            # WB stage control lines
            reg_write   = 1     # none (0) OR the corresponding reg is written (1)
            mem_to_reg  = 1     # write ALU data (0) OR memory data (1)

            # op code
            op = 35
            # rs
            rs = int(code_line[6:11].strip(), 2)
            # rt, the destination
            rt = int(code_line[11:16].strip(), 2)
            # immed
            # If sign bit is set, continue to two's comp
            if (int(code_line[16:32].strip(), 2) & (1 << (len(code_line[16:32].strip()) - 1))) != 0:
                immed = self.twos_comp(code_line[16:32].strip(), len(code_line[16:32].strip()))
            else:
                immed = int(code_line[16:32].strip(), 2)

            # Save to final instruction dictionary
            self.final_instruction['I%s' % index] = dict([('inst', 'LW'), ('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('immed',immed),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write),
                                                     ('mem_to_reg', mem_to_reg)])

        # Check if SW instruction, memory[rs + immed] := rt
        elif highest_six_bits == '101011':
            # Set control lines for SW
            # EX stage control lines
            alu_op      = '00'  # ALUOp1 = 0 and ALUOp0 = 0
            reg_read    = 1     # Always true, always reading from register
            # MEM stage control lines
            mem_read    = 0     # none (0), read data from memory address (1)
            mem_write   = 1     # none (0), write data to memory address (1)
            # WB stage control lines
            reg_write   = 0     # none (0) OR the corresponding reg is written (1)

            # op code
            op = 43
            # rs
            rs = int(code_line[6:11].strip(), 2)
            # rt, the destination
            rt = int(code_line[11:16].strip(), 2)
            # immed
            # If sign bit is set, continue to two's comp
            if (int(code_line[16:32].strip(), 2) & (1 << (len(code_line[16:32].strip()) - 1))) != 0:
                immed = self.twos_comp(code_line[16:32].strip(), len(code_line[16:32].strip()))
            else:
                immed = int(code_line[16:32].strip(), 2)

            # Save to final instruction dictionary
            self.final_instruction['I%s' % index] = dict([('inst', 'SW'), ('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('immed',immed),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write)])

        # Check if ADDI instruction, rt := rs + immed
        elif highest_six_bits == '001000':
            # Set control lines for ADDI
            # EX stage control lines
            alu_op      = '00'  # ALUOp1 = 0 and ALUOp0 = 0
            reg_read    = 1     # Always true, always reading from register
            # MEM stage control lines
            mem_read    = 0     # none (0), read data from memory address (1)
            mem_write   = 0     # none (0), write data to memory address (1)
            # WB stage control lines
            reg_write   = 1     # none (0) OR the corresponding reg is written (1)
            mem_to_reg  = 1     # write ALU data (0) OR memory data (1)

            # op code
            op = 8
            # rs
            rs = int(code_line[6:11].strip(), 2)
            # rt
            rt = int(code_line[11:16].strip(), 2)
            # immediate
            # If sign bit is set, continue to two's comp
            if (int(code_line[16:32].strip(), 2) & (1 << (len(code_line[16:32].strip()) - 1))) != 0:
                immed = self.twos_comp(code_line[16:32].strip(), len(code_line[16:32].strip()))
            else:
                immed = int(code_line[16:32].strip(), 2)

            # Save to final instruction dictionary
            self.final_instruction['I%s' % index] = dict([('inst', 'ADDI'), ('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('immed',immed),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write),
                                                     ('mem_to_reg', mem_to_reg)])

        # Check if BEQ instruction, if (rs = rt) then branch
        elif highest_six_bits == '000100':
            # Set control lines for BEQ
            # EX stage control lines
            alu_op      = '01'  # ALUOp1 = 0 and ALUOp0 = 1
            reg_read    = 1     # Always true, always reading from register
            # MEM stage control lines
            mem_read    = 0     # none (0), read data from memory address (1)
            mem_write   = 0     # none (0), write data to memory address (1)
            # WB stage control lines
            reg_write   = 0     # none (0) OR the corresponding reg is written (1)

            # op code
            op = 4
            # rs
            rs = int(code_line[6:11].strip(), 2)
            # rt, the destination
            rt = int(code_line[11:16].strip(), 2)
            # immed
            # If sign bit is set, continue to two's comp
            if (int(code_line[16:32].strip(), 2) & (1 << (len(code_line[16:32].strip()) - 1))) != 0:
                immed = self.twos_comp(code_line[16:32].strip(), len(code_line[16:32].strip()))
            else:
                immed = int(code_line[16:32].strip(), 2)

            # Save to final instruction dictionary
            self.final_instruction['I%s' % index] = dict([('inst', 'BEQ'), ('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('immed', immed),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write)])

        # Otherwise, BNE instruction, if (rs != rt) then branch
        elif highest_six_bits == '000101':
            # Set control lines for BNE
            # EX stage control lines
            alu_op      = '01'  # ALUOp1 = 0 and ALUOp0 = 1
            reg_read    = 1     # Always true, always reading from register
            # MEM stage control lines
            mem_read    = 0     # none (0), read data from memory address (1)
            mem_write   = 0     # none (0), write data to memory address (1)
            # WB stage control lines
            reg_write   = 0     # none (0) OR the corresponding reg is written (1)

            # op code
            op = 5
            # rs
            rs = int(code_line[6:11].strip(), 2)
            # rt, the destination
            rt = int(code_line[11:16].strip(), 2)
            # immed
            # If sign bit is set, continue to two's comp
            if (int(code_line[16:32].strip(), 2) & (1 << (len(code_line[16:32].strip()) - 1))) != 0:
                immed = self.twos_comp(code_line[16:32].strip(), len(code_line[16:32].strip()))
            else:
                immed = int(code_line[16:32].strip(), 2)

            # Save to final instruction dictionary
            self.final_instruction['I%s' % index] = dict([('inst', 'BNE'), ('op', op),
                                                     ('rs', rs),
                                                     ('rt', rt),
                                                     ('immed', immed),
                                                     ('alu_op', alu_op),
                                                     ('reg_read', reg_read),
                                                     ('mem_read', mem_read),
                                                     ('mem_write', mem_write),
                                                     ('reg_write', reg_write)])

        else:
            print 'ERROR: Unable to parse: ', code_line
            return 'EXIT'


    def twos_comp(self, val, bits):
        return int(val, 2) - (1 << bits)






