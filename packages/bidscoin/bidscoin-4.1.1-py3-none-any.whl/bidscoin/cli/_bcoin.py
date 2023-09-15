#!/usr/bin/env python3
"""
BIDScoin is a toolkit to convert and organize raw data-sets according to the Brain Imaging Data Structure (BIDS)

The basic workflow is to run these two tools:

  $ bidsmapper sourcefolder bidsfolder        # This produces a study bidsmap and launches a GUI
  $ bidscoiner sourcefolder bidsfolder        # This converts your data to BIDS according to the study bidsmap

Set the environment variable BIDSCOIN_DEBUG=TRUE in your console to run BIDScoin in its more verbose DEBUG logging mode

For more documentation see: https://bidscoin.readthedocs.io
"""

import argparse
import textwrap
from importlib.util import find_spec
if find_spec('bidscoin') is None:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parents[2]))
from bidscoin import version, bidsversion, bidsmap_template


def get_parser() -> argparse.ArgumentParser:
    """Build an argument parser with input arguments for bcoin.py"""

    localversion, uptodate, versionmessage = version(check=True)

    parser = argparse.ArgumentParser(prog='bidscoin',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent(__doc__),
                                     epilog='examples:\n'
                                            '  bidscoin -l\n'
                                            '  bidscoin -d data/bidscoin_tutorial\n'
                                            '  bidscoin -t\n'
                                            '  bidscoin -t my_template_bidsmap\n'
                                            '  bidscoin -b my_study_bidsmap\n'
                                            '  bidscoin -i data/my_template_bidsmap.yaml downloads/my_plugin.py\n ')
    parser.add_argument('-l', '--list',        help='List all executables (i.e. the apps, bidsapps and utilities)', action='store_true')
    parser.add_argument('-p', '--plugins',     help='List all installed plugins and template bidsmaps', action='store_true')
    parser.add_argument('-i', '--install',     help='A list of template bidsmaps and/or bidscoin plugins to install', nargs='+')
    parser.add_argument('-u', '--uninstall',   help='A list of template bidsmaps and/or bidscoin plugins to uninstall', nargs='+')
    parser.add_argument('-d', '--download',    help='Download folder. If given, tutorial MRI data will be downloaded here')
    parser.add_argument('-t', '--test',        help='Test the bidscoin installation and template bidsmap', nargs='?', const=bidsmap_template)
    parser.add_argument('-b', '--bidsmaptest', help='Test the run-items and their bidsnames of all normal runs in the study bidsmap. Provide the bids-folder or the bidsmap filepath')
    parser.add_argument('-v', '--version',     help='Show the installed version and check for updates', action='version', version=f"BIDS-version:\t\t{bidsversion()}\nBIDScoin-version:\t{localversion}, {versionmessage}")

    return parser
