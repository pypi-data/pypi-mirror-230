#!/usr/bin/env python

"""Shotfile reading with pure python

https://www.aug.ipp.mpg.de/aug/manuals/aug_sfutils

"""
__author__  = 'Giovanni Tardini (Tel. 1898)'
__version__ = '0.8.8'
__date__    = '11.09.2023'

import os, sys, logging, traceback

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')

logger = logging.getLogger('aug_sfutils')

if len(logger.handlers) == 0:
    hnd = logging.StreamHandler()
    hnd.setFormatter(fmt)
    logger.addHandler(hnd)

#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

logger.info('Using version %s', __version__)

try: # wrapper classes, available only with afs-client and kerberos access
    from .ww import *
except:
    traceback.print_exc()
    logger.warning('ww not loaded')
try:
    from .sfh import *
except:
    traceback.print_exc()
    logger.warning('sfh not loaded')
try:
    from .journal import *
except:
    traceback.print_exc()
    logger.warning('journal not loaded')

from .sfread import *
from .sf2equ import *
from .libddc import ddcshotnr, previousshot
from .mapeq import *
from .contour import *
try:
    from .getlastshot import getlastshot
except:
    traceback.print_exc()
    logger.warning('getlastshot not loaded')

sf_home = os.path.dirname(os.path.realpath(__file__))
logger.info('AUG-SF home %s', sf_home)
