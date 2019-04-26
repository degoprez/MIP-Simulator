class simulator(object):

    def hazard_detect_unit(self):
        # If I-type in ID/EX pipeline register, there cannot possibly be an error
        if self.pipeline_reg['ID/EX']['INSTR'] is None:
            self.string_to_print['ID_STAGE'] = 'I%d-ID' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            self.stall = False
            return

        # IF the data dependency instruct is SW, then no data hazard
        if (self.pipeline_reg['EX/MEM']['INSTR'] is not None):
            if self.pipeline_reg['EX/MEM']['INSTR']['op'] == 43:
                self.string_to_print['ID_STAGE'] = 'I%d-ID' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
                self.stall = False
                return
        if (self.pipeline_reg['MEM/WB']['INSTR'] is not None):
            if self.pipeline_reg['MEM/WB']['INSTR']['op'] == 43:
                self.string_to_print['ID_STAGE'] = 'I%d-ID' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
                self.stall = False
                return

        # If 1A or 1B type data hazard, then stall
        if (self.pipeline_reg['EX/MEM']['RD_REG'] == self.pipeline_reg['ID/EX']['RS_REG']) & \
                (self.pipeline_reg['EX/MEM']['RD_REG'] is not None) & \
                (self.pipeline_reg['ID/EX']['RS_REG'] is not None):
            self.stall = True
            self.string_to_print['ID_STAGE'] = 'I%d-stall' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            return
        elif (self.pipeline_reg['EX/MEM']['RD_REG'] == self.pipeline_reg['ID/EX']['RT_REG']) & \
                (self.pipeline_reg['EX/MEM']['RD_REG'] is not None) & \
                (self.pipeline_reg['ID/EX']['RT_REG'] is not None):
            self.stall = True
            self.string_to_print['ID_STAGE'] = 'I%d-stall' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            return

        # If 2A or 2B type data hazard, then stall
        elif (self.pipeline_reg['MEM/WB']['RD_REG'] == self.pipeline_reg['ID/EX']['RS_REG']) & \
                (self.pipeline_reg['MEM/WB']['RD_REG'] is not None) & \
                (self.pipeline_reg['ID/EX']['RS_REG'] is not None):
            self.stall = True
            self.string_to_print['ID_STAGE'] = 'I%d-stall' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            return
        elif (self.pipeline_reg['MEM/WB']['RD_REG'] == self.pipeline_reg['ID/EX']['RT_REG']) & \
                (self.pipeline_reg['MEM/WB']['RD_REG'] is not None) & \
                (self.pipeline_reg['ID/EX']['RT_REG'] is not None):
            self.stall = True
            self.string_to_print['ID_STAGE'] = 'I%d-stall' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            return
        else:
            self.string_to_print['ID_STAGE'] = 'I%d-ID' % self.pipeline_reg['IF/ID']['INSTR_INDEX']
            self.stall = False
            return

    def print_results(self):
        self.out_file.write('c#%d' % self.string_to_print['CC'])
        if self.string_to_print['WB_STAGE'] is not None:
            self.out_file.write(' ' + self.string_to_print['WB_STAGE'])
        if self.string_to_print['MEM_STAGE'] is not None:
            self.out_file.write(' ' + self.string_to_print['MEM_STAGE'])
        if self.string_to_print['EX_STAGE'] is not None:
            self.out_file.write(' ' + self.string_to_print['EX_STAGE'])
        if self.string_to_print['ID_STAGE'] is not None:
            self.out_file.write(' ' + self.string_to_print['ID_STAGE'])
        if self.string_to_print['IF_STAGE'] is not None:
            self.out_file.write(' ' + self.string_to_print['IF_STAGE'])

        self.out_file.write('\n')

        return

    def __init__(self, reg_file_in, memory_in, instructions_in, out_file):
        self.instructions = instructions_in
        self.memory = memory_in
        self.reg_file = reg_file_in

        self.out_file = out_file
        self.stall = False
        self.done = False

        self.branch_instr_index = 0

        self.branch = False
        self.branch_prev = False

        self.cc = 0

        self.string_to_print = {
            'CC' : 0,
            'IF_STAGE': None,
            'ID_STAGE': None,
            'EX_STAGE': None,
            'MEM_STAGE': None,
            'WB_STAGE': None
        }

        # initialize the 4 pipeline registers
        self.pipeline_reg = {
            'IF/ID': {'INSTR': None, 'TERM_SIG': 0, 'INSTR_INDEX':-1},
            'ID/EX': {'RS_REG': -1, 'RT_REG': -1, 'INSTR': None, 'TERM_SIG': 0, 'INSTR_INDEX':-1},
            'EX/MEM': {'RD_REG': -1, 'INSTR': None, 'RESULT': None, 'TERM_SIG': 0, 'INSTR_INDEX':-1},
            'MEM/WB': {'RD_REG': -1, 'INSTR': None, 'RESULT': None, 'TERM_SIG': 0, 'INSTR_INDEX':-1}
        }

        self.curr_instr_index = -1

        while True:
            self.WB()
            if self.done:
                return
            self.MEM()
            self.EX()
            self.ID()
            self.IF()

            self.cc += 1
            self.string_to_print['CC'] = self.cc
            # Write the results
            self.print_results()

    def IF(self):
        # reset branch signal if branching from MEM

        if self.branch_prev:
            # stall, if set, doesn't matter anymore, so reset
            self.stall = False
            self.branch_prev = False
            self.string_to_print['IF_STAGE'] = 'I%d-IF'
            # Fetch correct branched instruction
            if self.branch_instr_index < (len(self.instructions)):
                self.curr_instr_index = self.branch_instr_index
                self.pipeline_reg['IF/ID']['INSTR'] = self.instructions['I%s' % self.branch_instr_index]
                self.pipeline_reg['IF/ID']['RS_REG'] = self.instructions['I%s' % self.branch_instr_index]['rs']
                self.pipeline_reg['IF/ID']['RT_REG'] = self.instructions['I%s' % self.branch_instr_index]['rt']
                self.pipeline_reg['IF/ID']['INSTR_INDEX'] = self.branch_instr_index + 1
                self.string_to_print['IF_STAGE'] = 'I%d-IF' % (self.branch_instr_index + 1)
                return
        if self.branch:
            self.string_to_print['IF_STAGE'] = None
            self.pipeline_reg['IF/ID']['RS_REG'] = -1
            self.pipeline_reg['IF/ID']['RT_REG'] = -1
            self.pipeline_reg['IF/ID']['INSTR'] = None
            self.pipeline_reg['IF/ID']['TERM_SIG'] = 0
            self.branch_prev = True
            self.branch = False
            return

        # If stalling, do not change data
        if self.stall:
            self.string_to_print['IF_STAGE'] = None
            return
        # Fetch next instruction
        if self.curr_instr_index < len(self.instructions) - 1:
            self.curr_instr_index += 1
            self.pipeline_reg['IF/ID']['INSTR'] = self.instructions['I%s' % self.curr_instr_index]
            self.pipeline_reg['IF/ID']['RS_REG'] = self.instructions['I%s' % self.curr_instr_index]['rs']
            self.pipeline_reg['IF/ID']['RT_REG'] = self.instructions['I%s' % self.curr_instr_index]['rt']
            self.pipeline_reg['IF/ID']['INSTR_INDEX'] = self.curr_instr_index + 1
            self.string_to_print['IF_STAGE'] = 'I%d-IF' % (self.curr_instr_index + 1)
        else:
            self.string_to_print['IF_STAGE'] = None
            self.pipeline_reg['IF/ID']['RS_REG'] = -1
            self.pipeline_reg['IF/ID']['RT_REG'] = -1
            self.pipeline_reg['IF/ID']['INSTR'] = None
            self.pipeline_reg['IF/ID']['TERM_SIG'] = 1

    def ID(self):
        # Pass the terminate signal and the instruction number
        self.pipeline_reg['ID/EX']['TERM_SIG'] = self.pipeline_reg['IF/ID']['TERM_SIG']
        self.pipeline_reg['ID/EX']['INSTR_INDEX'] = self.pipeline_reg['IF/ID']['INSTR_INDEX']

        # If IF has not been run yet INSTR_INDEX = -1, then skip
        if self.pipeline_reg['ID/EX']['INSTR_INDEX'] == -1:
            self.pipeline_reg['ID/EX']['RS_REG'] = -1
            self.pipeline_reg['ID/EX']['RT_REG'] = -1
            self.pipeline_reg['ID/EX']['INSTR'] = None
            self.string_to_print['ID_STAGE'] = None
            return

        # If terminate signal is on
        if self.pipeline_reg['ID/EX']['TERM_SIG'] == 1:
            self.pipeline_reg['ID/EX']['RS_REG'] = -1
            self.pipeline_reg['ID/EX']['RT_REG'] = -1
            self.pipeline_reg['ID/EX']['INSTR'] = None
            self.string_to_print['ID_STAGE'] = None
            return

        # If MEM cycle branched, then flush
        if self.branch:
            self.pipeline_reg['ID/EX']['RS_REG'] = -1
            self.pipeline_reg['ID/EX']['RT_REG'] = -1
            self.pipeline_reg['ID/EX']['INSTR'] = None
            self.string_to_print['ID_STAGE'] = None
            return

        # if no instruction, continue
        if self.pipeline_reg['IF/ID']['INSTR'] is None:
            self.pipeline_reg['ID/EX']['RS_REG'] = -1
            self.pipeline_reg['ID/EX']['RT_REG'] = -1
            self.pipeline_reg['ID/EX']['INSTR'] = None
            self.string_to_print['ID_STAGE'] = None
            return

        # If stalling, do not change data, return
        if self.stall:
            # check if there is still a data hazard, if not, turn of the hazard signal
            self.hazard_detect_unit()
            return

        self.pipeline_reg['ID/EX']['INSTR'] = self.pipeline_reg['IF/ID']['INSTR']

        self.pipeline_reg['ID/EX']['RS_REG'] = self.pipeline_reg['IF/ID']['INSTR']['rs']
        self.pipeline_reg['ID/EX']['RT_REG'] = self.pipeline_reg['IF/ID']['INSTR']['rt']

        # Hazard detection unit
        self.hazard_detect_unit()
        return

    def EX(self):
        # Pass the terminate signal
        self.pipeline_reg['EX/MEM']['TERM_SIG'] = self.pipeline_reg['ID/EX']['TERM_SIG']
        self.pipeline_reg['EX/MEM']['INSTR_INDEX'] = self.pipeline_reg['ID/EX']['INSTR_INDEX']

        if self.pipeline_reg['EX/MEM']['TERM_SIG'] == 1:
            self.string_to_print['EX_STAGE'] = None
            return

        # if MEM cycle branched, then flush
        if self.branch:
            self.pipeline_reg['EX/MEM']['RD_REG'] = -1
            self.pipeline_reg['EX/MEM']['INSTR'] = None
            self.pipeline_reg['EX/MEM']['RESULT'] = None
            self.string_to_print['EX_STAGE'] = None
            return

        # if no instruction, continue bubble
        if self.pipeline_reg['ID/EX']['INSTR'] is None:
            self.pipeline_reg['EX/MEM']['RS_REG'] = -1
            self.pipeline_reg['EX/MEM']['RT_REG'] = -1
            self.pipeline_reg['EX/MEM']['INSTR'] = None
            self.string_to_print['EX_STAGE'] = None
            return

        # stall if data hazard, then feed nop, do not grab ID/EX content
        if self.stall:
            self.pipeline_reg['EX/MEM']['RD_REG'] = -1
            self.pipeline_reg['EX/MEM']['INSTR'] = None
            self.pipeline_reg['EX/MEM']['RESULT'] = None
            self.string_to_print['EX_STAGE'] = None #TODO potentialy incorrect
            return

        instruction = self.pipeline_reg['ID/EX']['INSTR']

        # Check if R-type instruction
        if instruction['op'] == 0:
            # Check func code
            if instruction['func'] == 42:   # SLT
                result = self.reg_file['R%s' % instruction['rs']] < \
                         self.reg_file['R%s' % instruction['rt']]
            elif instruction['func'] == 32:   # ADD
                result = self.reg_file['R%s' % instruction['rs']] + \
                         self.reg_file['R%s' % instruction['rt']]
            elif instruction['func'] == 34:   # SUB
                result = self.reg_file['R%s' % instruction['rs']] - \
                         self.reg_file['R%s' % instruction['rt']]
            else:
                print 'ERROR: Unknown function code:', instruction['func']
                return
            self.pipeline_reg['EX/MEM']['RESULT'] = result
            self.pipeline_reg['EX/MEM']['RD_REG'] = instruction['rd']
            self.pipeline_reg['EX/MEM']['INSTR'] = instruction
            self.string_to_print['EX_STAGE'] = 'I%d-EX' % self.pipeline_reg['ID/EX']['INSTR_INDEX']

        # Otherwise, it is an I-type instruction
        else:
            # Check op code
            if instruction['op'] == 35:   # LW
                result = self.reg_file['R%s' % instruction['rs']] + instruction['immed'] * 4
            elif instruction['op'] == 43:   # SW
                result = self.reg_file['R%s' % instruction['rs']] + instruction['immed'] * 4
            elif instruction['op'] == 8:    # ADDI
                result = self.reg_file['R%s' % instruction['rs']] + instruction['immed']
            elif instruction['op'] == 4:    # BEQ
                result = self.reg_file['R%s' % instruction['rs']] == \
                         self.reg_file['R%s' % instruction['rt']]
                # If BEQ branch should be taken, flush previous stages, and increment instr index
                if result:
                    self.branch = True
                    # Increment instruction index to the new branched instruction
                    self.branch_instr_index = self.curr_instr_index + instruction['immed']

                    # Insert bubble, but keep branch instruction
                    self.pipeline_reg['EX/MEM']['RD_REG'] = -1
                    self.pipeline_reg['EX/MEM']['INSTR'] = instruction
                    self.pipeline_reg['EX/MEM']['RESULT'] = None
                    self.string_to_print['EX_STAGE'] = 'I%d-EX' % \
                                                       self.pipeline_reg['ID/EX']['INSTR_INDEX']
                    return

            elif instruction['op'] == 5:    # BNE
                result = self.reg_file['R%s' % instruction['rs']] != \
                         self.reg_file['R%s' % instruction['rt']]
                # If BNE branch should be taken, flush previous stages, and increment instr index
                if result:
                    self.branch = True
                    # Set the branch instruction index to the new branched instruction
                    self.branch_instr_index = self.curr_instr_index + instruction['immed']

                    # Insert bubble, but keep branch instruction
                    self.pipeline_reg['EX/MEM']['RD_REG'] = -1
                    self.pipeline_reg['EX/MEM']['INSTR'] = instruction
                    self.pipeline_reg['EX/MEM']['RESULT'] = None
                    self.string_to_print['EX_STAGE'] = 'I%d-EX' % \
                                                       self.pipeline_reg['ID/EX']['INSTR_INDEX']
                    return
            else:
                print 'ERROR: Unkown function code:', instruction['func']
                return

            self.pipeline_reg['EX/MEM']['RESULT'] = result
            self.pipeline_reg['EX/MEM']['RD_REG'] = instruction['rt']
            self.pipeline_reg['EX/MEM']['INSTR'] = instruction
            self.string_to_print['EX_STAGE'] = 'I%d-EX' % self.pipeline_reg['ID/EX']['INSTR_INDEX']

    def MEM(self):
        # Pass the terminate signal
        self.pipeline_reg['MEM/WB']['TERM_SIG'] = self.pipeline_reg['EX/MEM']['TERM_SIG']
        self.pipeline_reg['MEM/WB']['INSTR_INDEX'] = self.pipeline_reg['EX/MEM']['INSTR_INDEX']

        # If terminate signal on, do nothing
        if self.pipeline_reg['MEM/WB']['TERM_SIG'] == 1:
            self.string_to_print['MEM_STAGE'] = None
            return

        # Bubble happened b/c of previous stall
        if self.pipeline_reg['EX/MEM']['INSTR'] is None:
            self.pipeline_reg['MEM/WB']['RD_REG'] = -1
            self.pipeline_reg['MEM/WB']['INSTR'] = None
            self.pipeline_reg['MEM/WB']['RESULT'] = None
            self.string_to_print['MEM_STAGE'] = None
            return

        instruction = self.pipeline_reg['EX/MEM']['INSTR']
        result = self.pipeline_reg['EX/MEM']['RESULT']
        rd = self.pipeline_reg['EX/MEM']['RD_REG']

        # If branch, skip stage
        if instruction['op'] == 4 or instruction['op'] == 5:
            self.pipeline_reg['MEM/WB']['RD_REG'] = -1
            self.pipeline_reg['MEM/WB']['INSTR'] = instruction
            self.pipeline_reg['MEM/WB']['RESULT'] = None
            self.string_to_print['MEM_STAGE'] = 'I%d-MEM' % self.pipeline_reg['EX/MEM']['INSTR_INDEX']
            return

        # If R-type, skip MEM stage
        if instruction['op'] == 0:
            # Forward results
            self.pipeline_reg['MEM/WB']['RD_REG'] = rd
            self.pipeline_reg['MEM/WB']['INSTR'] = instruction
            self.pipeline_reg['MEM/WB']['RESULT'] = result
            self.string_to_print['MEM_STAGE'] = 'I%d-MEM' % self.pipeline_reg['EX/MEM']['INSTR_INDEX']
            return
        # Otherwise, I-type
        elif instruction['op'] == 35: # LW
            self.pipeline_reg['MEM/WB']['RESULT'] = self.memory[result]
            self.pipeline_reg['MEM/WB']['INSTR'] = instruction
            self.pipeline_reg['MEM/WB']['RD_REG'] = rd
            self.string_to_print['MEM_STAGE'] = 'I%d-MEM' % self.pipeline_reg['EX/MEM']['INSTR_INDEX']
            return
        elif instruction['op'] == 43: #SW
            self.memory[result] = self.reg_file['R%s' % (rd)]
            # Job is done here if SW instruction
            self.pipeline_reg['MEM/WB']['RD_REG'] = rd
            self.pipeline_reg['MEM/WB']['INSTR'] = instruction
            self.pipeline_reg['MEM/WB']['RESULT'] = None
            self.string_to_print['MEM_STAGE'] = 'I%d-MEM' % self.pipeline_reg['EX/MEM']['INSTR_INDEX']
            return
        elif instruction['op'] == 8: #ADDI
            # Forward results
            self.pipeline_reg['MEM/WB']['RD_REG'] = rd
            self.pipeline_reg['MEM/WB']['INSTR'] = instruction
            self.pipeline_reg['MEM/WB']['RESULT'] = result
            self.string_to_print['MEM_STAGE'] = 'I%d-MEM' % self.pipeline_reg['EX/MEM']['INSTR_INDEX']
            return


    def WB(self):
        # Pass the instruction number
        instr_index = self.pipeline_reg['MEM/WB']['INSTR_INDEX']

        # Check if terminate signal is on
        if self.pipeline_reg['MEM/WB']['TERM_SIG']:
            self.done = True
            self.string_to_print['WB_STAGE'] = None
            return

        if self.pipeline_reg['MEM/WB']['INSTR'] is None:
            # If there's a bubble, return
            self.string_to_print['WB_STAGE'] = None
            return

        instruction = self.pipeline_reg['MEM/WB']['INSTR']
        result = self.pipeline_reg['MEM/WB']['RESULT']
        rd = self.pipeline_reg['MEM/WB']['RD_REG']

        # If branch, skip stage
        if instruction['op'] == 4 or instruction['op'] == 5:
            self.string_to_print['WB_STAGE'] = 'I%d-WB' % self.pipeline_reg['MEM/WB']['INSTR_INDEX']
            return

        # If R-type, write back
        if instruction['op'] == 0:
            self.reg_file['R%s' % rd] = result
        # If LW instruct
        elif instruction['op'] == 35:
            self.reg_file['R%s' % rd] = result
        # If ADDI instruct
        elif instruction['op'] == 8:
            self.reg_file['R%s' % rd] = result

        self.string_to_print['WB_STAGE'] = 'I%d-WB' % self.pipeline_reg['MEM/WB']['INSTR_INDEX']



