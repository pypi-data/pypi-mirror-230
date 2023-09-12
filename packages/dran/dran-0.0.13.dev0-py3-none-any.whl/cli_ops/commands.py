
# ============================================================================#
# File: commands.py                                                     #
# Author: Pfesesani V. van Zyl                                                #
# ============================================================================#

# Standard library imports
# --------------------------------------------------------------------------- #
import sys

# Local imports
# --------------------------------------------------------------------------- #
sys.path.append("src/")
from common.messaging import msg_wrapper
# =========================================================================== #


class Command:

    # 
    def __init__(self):
        print()
        self.commands={}
        self.get_commands()
        # cmdList=['read','show','bf','pf','fit','cs','exit','pl','cmds','reset']
        self.cmdList=['read','show','bf','pf','fit','cs','exit','pl','cmds','reset']
        # pass

    def get_commands(self):

        """ list of all available commands"""
        self.read()
        self.show()
        self.bf()
        self.pf()
        self.fit()
        self.cs()
        self.exit()
        self.pl()
        self.cmds()
        self.reset()

        # for k,v in self.commands.items():
        #     print(k,v['use'])
        #     print()

        
    def cmds(self):
        cmd = 'cmds'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'cmds'
        self.commands[cmd]['shortdesc'] = 'get list of all commands'
        self.commands[cmd]['desc'] = '\n cmds \n\n Show list of valid commands.'


    def read(self):
        cmd = 'read'
        self.commands[cmd] = {'use':'read [filename or filepath]',
                              'shortdesc': 'read in a file',
                              'desc':'\n read [filename or filepath] \
                                  \n\n e.g read data/HydraA_13NB/2011d125_15h12m33s_Cont_mike_HYDRA_A.fits\
                                  \n\n Read drift scan data from the file given.\
                                  \n If the filename is not given as part of the command string,\
                                   \n the user is prompted for the filename parameter. \
                                    \n The filename parameter[filename or filepath] is the name \
                                    \n or full path of the file to read from. It is \
                                    \n assumed the file name/path is not given at the start \
                                    \n of the program. Please review code documentation for more info.'}
    

    def reset(self):
        cmd='reset'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'reset'
        self.commands[cmd]['shortdesc'] = 'reset all parameters to default settings'
        self.commands[cmd]['desc'] = 'reset  \n\Reset data to default values. \
            \n Deletes all previously fit data and sets the data to those of \
            \n the original drift scan file.'


    def show(self):
        cmd='show'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'show '
        self.commands[cmd]['shortdesc'] = 'display the file extracted parameters'
        self.commands[cmd]['desc'] = 'show  \n\nShow all the parameters that were extracted from the file. This prints out a dictionary\n\n of all the source parameters of interest of a given source.\n\nExample:\n\nshow\n\n You can also show parameters that have already been established like the baseline fit points, the peak fit pointa and the current scan being processed\n\nExample:\n\nshow bf\n\nshow pf \n\nshow scan'


    def bf(self):
        cmd='bf'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'bf [list of points to fit] order'
        self.commands[cmd]['shortdesc'] = 'list all fitting blocks'
        self.commands[cmd]['desc'] = """bf [list of points to fit] order\n\nSet the start and end  blocks for fitting a polynomial to


        the baseline of a spectrum.

        If PB is entered without parameters, the current values are shown
        and the user is prompted for another start, end velocity pair.

        If PB is entered with start and end velocities, these are added to the
        current list of start, end pairs.

        If SHOW is given as the second parameter, the current values are shown.

        If CLEAR is given as the second parameter, all values are cleared.

        Baseline block limits must be set prior to an automated polynomial fit.
        These may be present from a previous fit, and can be seen using PB SHOW
        otherwise they must be entered using PB, or set via a previous PO fit.+

        After carrying out a polynomial fit, the baseline blocks that were used
        are stored and can be reused.  Executing PB after PO will show the start
        and end values of each block.  This can be exploited when processing many
        spectra of the same source:
        * use RAV to average many or all of the spectra, to obtain a high
        signal to noise ratio and show up weak features
        * use PO to fit a polynomial to the average spectrum
        * use a DO loop to:
            * read the individual spectra
                * fit polynomials to the spectra using PO with PB option
                * write out each spectrum to a new file

        example:

        pb - 100 - 45
        pb - 30 - 10
        pb 0.5 90"""

    def pf(self):
        cmd = 'pf'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'pf [list of points to fit] order'
        self.commands[cmd]['shortdesc'] = 'give the locations where the fit is to be performed'
        self.commands[cmd]['desc'] = """pf [list of points to fit] order\n\nSet the start and end velocities of blocks for fitting a polynomial to


        the baseline of a spectrum.

        If PB is entered without parameters, the current values are shown
        and the user is prompted for another start, end velocity pair.

        If PB is entered with start and end velocities, these are added to the
        current list of start, end pairs.

        If SHOW is given as the second parameter, the current values are shown.

        If CLEAR is given as the second parameter, all values are cleared.

        Baseline block limits must be set prior to an automated polynomial fit.
        These may be present from a previous fit, and can be seen using PB SHOW
        otherwise they must be entered using PB, or set via a previous PO fit.+

        After carrying out a polynomial fit, the baseline blocks that were used
        are stored and can be reused.  Executing PB after PO will show the start
        and end values of each block.  This can be exploited when processing many
        spectra of the same source:
        * use RAV to average many or all of the spectra, to obtain a high
        signal to noise ratio and show up weak features
        * use PO to fit a polynomial to the average spectrum
        * use a DO loop to:
            * read the individual spectra
                * fit polynomials to the spectra using PO with PB option
                * write out each spectrum to a new file

        example:

        pb - 100 - 45
        pb - 30 - 10
        pb 0.5 90"""

    def fit(self):
        """ Fit """
        cmd = 'fit'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'fit [list of points to fit] order'
        self.commands[cmd]['shortdesc'] = 'perform a polynomial fit on the listed data points'
        self.commands[cmd]['desc'] = """fit [list of points to fit] order\n\nSet the start and end velocities of blocks for fitting a polynomial to


        the baseline of a spectrum.

        If PB is entered without parameters, the current values are shown
        and the user is prompted for another start, end velocity pair.

        If PB is entered with start and end velocities, these are added to the
        current list of start, end pairs.

        If SHOW is given as the second parameter, the current values are shown.

        If CLEAR is given as the second parameter, all values are cleared.

        Baseline block limits must be set prior to an automated polynomial fit.
        These may be present from a previous fit, and can be seen using PB SHOW
        otherwise they must be entered using PB, or set via a previous PO fit.+

        After carrying out a polynomial fit, the baseline blocks that were used
        are stored and can be reused.  Executing PB after PO will show the start
        and end values of each block.  This can be exploited when processing many
        spectra of the same source:
        * use RAV to average many or all of the spectra, to obtain a high
        signal to noise ratio and show up weak features
        * use PO to fit a polynomial to the average spectrum
        * use a DO loop to:
            * read the individual spectra
                * fit polynomials to the spectra using PO with PB option
                * write out each spectrum to a new file

        example:

        pb - 100 - 45
        pb - 30 - 10
        pb 0.5 90"""

    def cs(self):
        """ change scan """
        cmd = 'cs'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'cs 1'
        self.commands[cmd]['shortdesc'] = 'change drift-scan'
        self.commands[cmd]['desc'] = '''cs \n\nChange the scan that is currently 
        being processed. By default, upon opening a file the scan number is 0
        which can indicate one of the following.
        
        For low frequencies e.g. 2280 MHz, there are only 2 scans, 
        ONLCP = 0
        ONRCP = 1
        
        For higher frequencies with 6 scans,  
        HPSLCP = 0
        HPNLCP = 1
        ONLCP = 2
        HPSRCP = 3
        HPNRCP = 4
        ONRCP = 5
        
        \n\nExample:\n\ncs 1'''

    def exit(self):
        """ quit the program. """
        cmd='exit'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'exit'
        self.commands[cmd]['shortdesc'] = 'exit the program'
        self.commands[cmd]['desc'] = 'exits the program\n'  
        
    def pl(self):
        """ plot the data. """
        
        cmd='pl'
        self.commands[cmd] = {}
        self.commands[cmd]['use'] = 'pl '
        self.commands[cmd]['shortdesc'] = 'plot the data'
        self.commands[cmd]['desc'] = 'plot the data\n' 