#!/usr/bin/python
# =========================================================================== #
# -*- coding: utf-8 -*-                                                       #
# Project : HartRAO's 26m telescope data reduction and analysis program.      #
# File    : dran.py                                                           #
# Author  : Pfesesani V. van Zyl                                              # 
# Date    : 01/01/2016                                                        #
# Version : 1.0                                                               #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #

import os
from sys import argv, stderr, exit
import argparse
import warnings

# handle/ignore python warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

# Local imports
# --------------------------------------------------------------------------- #

def run(args):
    """
    Command line interface for dran.
    
    Loads the command name and parameters from :py:data:'argv'.
    """

    print(len(argv), argv)
    if len(argv) > 1:
        pass
    #     command_name = argv[1]

    #     try:
    #         command_type = registered_commands[command_name]
    #     except KeyError:
    #         if command_name not in ('-h', '--help'):
    #             stderr.write('Unknown command {}\n'.format(command_name))
    #         pass

    # command = command_type()
    # return command.run(**command.configure(argv[2:]))
    else:
        pass

    print("Hello DRAN")

def main():
    """
    Command line interface for dran.
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran -h
    """

    parser = argparse.ArgumentParser(prog='DRAN-AUTO', 
        description="Begin processing HartRAO drift scan data")
    parser.add_argument("-docs", help="Opens the documentation browser", default = "y",type=str, required=False)
    # parser.add_argument("-auto", help="process file or folder at given path e.g. -f data/HydraA_13NB/2019d133_16h12m15s_Cont_mike_HYDRA_A.fits or -f data/HydraA_13NB", type=str, required=False)
    # # parser.add_argument("-force", help="force fit all drift scans y/n e.g. -force y. Default is set to n", type=str, required=False)
    # parser.add_argument("-delete_db", help="delete database on program run. e.g. -delete_db all or -delete_db CALDB.db", type=str, required=False)
    
    parser.add_argument('--version', action='version', version='%(prog)s {__version__}')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

