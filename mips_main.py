#!/usr/env/bin python
import sys
import instruction_parser
import simulator


if __name__ == "__main__":

    while True:

        input_file_name = raw_input("Input filename: ")
        output_file_name = raw_input("Output filename: ")

        with open(input_file_name, 'r') as in_file:
            content = in_file.readlines()

        out_file = open(output_file_name, 'w')

        # remove whitespace
        content = [x.strip() for x in content]

        parsed_instructions = instruction_parser.instruction_parser(content)
        if parsed_instructions == 'EXIT':
            print 'ERROR: could not parse the input file'
            in_file.close()
            out_file.close()
            exit()

        res = simulator.simulator(parsed_instructions.register_file, parsed_instructions.memory, parsed_instructions.final_instruction, out_file)

        out_file.write('REGISTERS\n')
        for i in range(len(res.reg_file)):
            if res.reg_file['R%d' % i] != 0:
                out_file.write('R%d %d' % (i, res.reg_file['R%d' % i]) + '\n')

        out_file.write('MEMORY\n')
        for i in range(1000 / 4):
            if res.memory[i * 4] != 0:
                out_file.write('%d %d' % (i * 4, res.memory[i * 4]) + '\n')

        continue_bool = raw_input("Repeat? (y/n) ")
        if 'n' in continue_bool:
            in_file.close()
            out_file.close()
            exit()


