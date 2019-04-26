# MIPS-Pipelined-Simulator
Simulates a pipelined MIPS CPU 

This MIPS simulator is capable of loading a specified file containing a sequence of MIPS binaries, and outputting the program computation outputs.

Example input and output files are provided (input.txt, output.txt). 

# Details
This program was written in Python 2.7.12 and was developed inside a Linux OS (Ubuntu 16.04)

# Run the Program
To run the program enter `python mips_main.py` The program will then prompt the user for the file
input name and the desired output name. The progam is run iteratively and can be canceled by the user.

# Troubleshooting
If `python mips_main.py` doesn't work, try the following

```
chmod u+x mips_main.py
./mips_main.py

```
If the program is unable to parse your file, make sure your `.txt` input files were created inside a `Linux OS`. If they weren't, create a new `.txt` file inside a Linux OS and copy the contents of the previous text file into the new one.

# Dependencies
None

# Contact
If you have any questions, please contact me @

Diego Perez
degoprez@gmail.com


