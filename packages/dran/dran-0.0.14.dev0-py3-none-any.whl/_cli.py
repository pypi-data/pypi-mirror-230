# The command line interface of dran
# ============================================================================#
# File: cli.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
import os
import sys
from sys import argv
import argparse

# Local imports
# --------------------------------------------------------------------------- #
from common.messaging import msg_wrapper, print_start, load_prog
from common.misc_funcs import delete_logs
from cli_ops.commands import Command

# initialize parameters
# PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

class CLI:

    def __init__(self,log="",filePath=""):
        # "Command Line Interface initiated.\n"
        
        self.cmds = Command # INITIALIZE COMMANDS
        commands=[]

        self.prompt="\nDRAN $ "

        print()
        os.system('pwd')
        inp=input(f"{self.prompt}Type 'help' to get help, otherwise get started\n")
        if inp=='h' or inp=="-h" or inp=="help":
            self.print_help()
        else:
            pass

        
        # print(self.cmds)

    def list_commands(self):
        print(self.cmds.cmdList)

    def print_help(self):
        """ print help message"""
        print(f"{self.prompt} DRAN is a data reduction and analysis software pipeline developed to \nsystematically reduce and analyze HartRAO's 26m single dish data. The \ndata can be reduced in a number of ways.\n\n1. You can automatically reduce the data by exiting this CLI window and \ntyping \n\n>> dran-auto full_path_to_your_file \n\n2. Using the GUI by typing \n\n>> dran-gui \n\n3. Using the CLI (this window), by typing\n\n>> command_name [command_parameters] e.g read hydraA_13NB_file.fits \n\nThe command parameters for any command can be viewed by typing \n\n>> cmds\n\nIf you would like to view a command description, this can be done through\n\n>> command_name desc\n\nTo see the usage of a specific command you can also type \n\n>> command_name use\n\nTo get more info on the commands you can also view the documentation\n\n>> dran docs\n\nor see the README.md file provided with the code. You can also see \n\n>> dran -h \n\nfor other features that come with the program. If all else fails you can \nemail the author pfesi24@gmail.co.za\n")


def main():
    """
    Command line interface for dran.
    
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran -h
    """

    if len(argv) == 1:
        load_prog("CLI - Command Line Interface")
        print_start()
        delete_logs()
        CLI()
        print()

    # elif len(argv) == 2:
    #     # given a filename or folder name process the data
    #     readFile= os.path.isfile(argv[1])

    #     if readFile==True:
    #         print(f"Processing file {argv[1]}")
    #     else:
    #         print("Loading cli")
    #         cli = CLI()
    #         # readFolder= os.path.isdir(argv[1])
    #         # if readFolder==True:
    #         #     print(f"Processing files in folder {argv[1]}")
    #         # else:
    #         #     print(f"{argv[1]} is not a file nor a folder, try again")
    #         #     sys.exit()
    else:
        print("Too many inputs given")

if __name__ == "__main__":
    main()


