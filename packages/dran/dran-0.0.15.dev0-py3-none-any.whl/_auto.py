# ============================================================================#
# File: _auto.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
# The automated part of dran
import os
import sys
from sys import argv
import argparse

# Local imports
# --------------------------------------------------------------------------- #
# from common import __ # __version__
from inits import __version__, logfile
from common.messaging import msg_wrapper, load_prog
from common.misc_funcs import delete_logs
from cli_ops.commands import Command
from common.log_conf import configure_logging
from common.process_selection import ProcessSelector
from common.load_prog import LoadProg


def run(args):
    
    # initiate and configure logging
    delete_logs() # delete any previously generated logfiles
    log = configure_logging()

    load_prog("Automated processing")

    LoadProg(args,log)

    if args.f:

        # start the automated program

        # given a filename or folder name process the data
        readFile= os.path.isfile(args.f)
        readFolder= os.path.isdir(args.f)

        if readFile==True:
            msg_wrapper("info",log.info,f"Attempting to process file {args.f}")
            ProcessSelector(args.f, autoKey=1,log=log)
            print()

        elif readFolder==True and readFolder != "../":
            print(f"Attempting to process files in folder {args.f}")
            ProcessSelector(args.f, autoKey=2,log=log)
        else:
            print(f"{args.f} \nis neither an acceptable file nor folder, pleasengo through the documentation to undestand the permitted files/folders and try again\n")
            sys.exit()
    else:
        print("\nNo arguments added, closing program\n")

def main():
    """
    Command line interface for dran.
    Loads the command name and parameters from :py:data:'argv'.

    Usage:
        dran -h
    """

    parser = argparse.ArgumentParser(prog='DRAN-AUTO', 
        description="Begin processing HartRAO drift scan data")
    parser.add_argument("-db", help="turn debugging on or off. e.g. -db on, by default debug is off", type=str, required=False)
    parser.add_argument("-f", help="process file or folder at given path e.g. -f data/HydraA_13NB/2019d133_16h12m15s_Cont_mike_HYDRA_A.fits or -f data/HydraA_13NB", type=str, required=False)
    parser.add_argument("-delete_db", help="delete database on program run. e.g. -delete_db all or -delete_db CALDB.db", type=str, required=False)
    parser.add_argument("-conv", help="convert database tables to csv. e.g. -conv CALDB", type=str,required=False)
    parser.add_argument("-quickview", help="get quickview of data e.g. -quickview y", type=str.lower, required=False, choices=['y', 'yes'], )
    parser.add_argument('-version', action='version', version='%(prog)s'+f' {__version__}')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()