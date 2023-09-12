import os, datetime, logging
import numpy as np

from aug_sfutils import sfmap, sfobj, manage_ed, parse_kwargs, str_byt, libddc, getlastshot
from aug_sfutils.shotfile import SHOTFILE as SF


logger = logging.getLogger('aug_sfutils.sfread')
date_fmt = '%Y-%m-%d'
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

LONGLONG = sfmap.typeMap('descr', 'SFfmt', 'LONGLONG')


def read_other_sf(*args, **kwargs):

    return SFREAD(*args, **kwargs)


def getcti_ts06(nshot):
    """Gets the absolute time (ns) of a discharge trigger"""

    diag = 'CTI'
    cti = SFREAD(nshot, diag)

    try:
        cdev = cti.getparset('LAM')
        ts06 = cdev['PhyReset']
        if ts06 == 0:
            ts06 = cdev['TS06']
        if ts06 == 0:
            ts06 = cdev['CT_TS06']
    except: # shot < 35318
        cdev = cti.getparset('TS6')
        ts06 = cdev['TRIGGER']
        logger.debug('getcti_ts06 %d', ts06)
    if ts06 < 1e15:
        ts06 = None
    return ts06



class SFREAD:
    """
    Class for reading ASDEX Upgrade shotfile data
    """

    def __init__(self, *args, **kwargs):
        """
        Opens a shotfile, reads the header
        """

        self.shot = None
        self.diag = None
        self.exp = None
        self.status = False
        self.open(*args, **kwargs)
        if len(args) > 2:
            logger.warning('More than 2 explicit arguments: only the first two (diag, shot) are retained')


    def open(self, *args, **kwargs):

        if 'sfh' in kwargs.keys():
            self.sfpath = kwargs['sfh']
            self.shot = 0
            self.ed = 0
            self.diag = os.path.basename(self.sfpath)[:3]

        elif 'sf' in kwargs.keys():
            self.sfpath = os.path.abspath(kwargs['sf'])
            dirs = self.sfpath.split('/')[::-1]
            sshot = ''
            for subdir in dirs:
                try:
                    a = float(subdir)
                    sshot = subdir + sshot
                except:
                    self.diag = subdir
                    break
            self.shot = int(sshot.split('.')[0])

        else:

            n_args = len(args)
            if n_args == 0:
                logger.warning('No argument given, need at least diag_name')
                return
            if isinstance(args[0], str) and len(args[0].strip()) == 3:
                diag = args[0].strip()
                if n_args > 1:
                    if isinstance(args[1], (int, np.integer)):
                        nshot = args[1]
            elif isinstance(args[0], (int, np.integer)):
                nshot = args[0]
                if n_args > 1:
                    if isinstance(args[1], str) and len(args[1].strip()) == 3:
                        diag = args[1].strip()
            if 'nshot' not in locals():
                logger.warning('No argument is a shot number (int), taking last AUG shot')
                nshot = getlastshot.getlastshot()
            if 'diag' not in locals():
                diag = input('Please enter a diag_name (str(3), no delimiter):\n')

            exp = parse_kwargs.parse_kw( ('exp', 'experiment'), kwargs, default='AUGD')
            ed  = parse_kwargs.parse_kw( ('ed', 'edition'), kwargs, default=0)
            logger.debug('%d %s %s %d', nshot, diag, exp, ed)
            self.sfpath, self.ed = manage_ed.sf_path(nshot, diag, exp=exp, ed=ed)
            if self.sfpath is None:
                logger.error('Shotfile not found for %s:%s(%d) #%d', exp, diag, ed, nshot)
                return
            else:
                self.shot = nshot
                self.diag = diag.upper()
                self.exp  = exp  # unused herein, but useful docu

        logger.debug('Shotfile path: %s', self.sfpath)
        if os.path.isfile(self.sfpath):
            self.time = datetime.datetime.fromtimestamp(os.path.getctime(self.sfpath))
        else:
            logger.error('Shotfile %s not found' %self.sfpath)
            return

        logger.info('Fetching SF %s', self.sfpath)
        self.sf = SF(self.sfpath)
        self.status = (self.sf is not None)

        self.cache = {}


    def __call__(self, name):

        if not self.status:
            return None

        SFOlbl = self.sf[name].SFOtypeLabel
        if SFOlbl == 'ParamSet':
            return self.getparset(name)

        if name not in self.cache.keys():
            if SFOlbl in sfmap.DataObjects:
                self.cache[name] = self.getobject(name)
            else:
                logger.error('Signal %s:%s not found for shot #%d', self.diag, name, self.shot)
                return None
        return self.cache[name]


    def gettimebase(self, obj, tbeg=None, tend=None, cal=True):
        """
        Reads the timebase of a given SIG, SGR or AB
        """

        obj = str_byt.to_str(obj)
        if obj not in self.sf.keys():
            logger.error('Sig/TB %s:%s not found for #%d', self.diag, obj, self.shot)
            return None
        sfo = self.sf[obj]

        if sfo.SFOtypeLabel == 'TimeBase':
            return self.getobject(obj, tbeg=tbeg, tend=tend, cal=cal)
        elif sfo.SFOtypeLabel in ('SignalGroup', 'Signal', 'AreaBase'):
            for rel in sfo.relations:
                if self.sf[rel].SFOtypeLabel == 'TimeBase':
                    return self.getobject(rel, tbeg=tbeg, tend=tend, cal=cal)
        return None


    def getareabase(self, obj, tbeg=None, tend=None):
        """
        Reads the areabase of a given SIG or SGR
        """

        obj = str_byt.to_str(obj)
        if obj not in self.sf.keys():
            logger.error('Sig/AB %s:%s not found for #%d', self.diag, obj, self.shot)
            return None
        sfo = self.sf[obj]

        if sfo.SFOtypeLabel == 'AreaBase':
            return self.getobject(obj, tbeg=tbeg, tend=tend)
        elif sfo.SFOtypeLabel in ('SignalGroup', 'Signal'):
            for rel in sfo.relations:
                if self.sf[rel].SFOtypeLabel == 'AreaBase':
                    return self.getobject(rel, tbeg=tbeg, tend=tend)
        return None


    def getobject(self, obj, cal=True, nbeg=0, nend=None, tbeg=None, tend=None):
        """
        Reads the data of a given TB, AB, SIG or SGR
        """

        obj = str_byt.to_str(obj)
        data = None
        if obj not in self.sf.keys():
            logger.error('Signal %s:%s not found for #%d', self.diag, obj, self.shot)
            return None

# Keep commented, to allow 1 cal and 1 uncal reading
#        if obj in self.cache.keys():
#            return cache[obj]

        sfo = self.sf[obj]
        if sfo.status != 0:
            logger.error('Status of SF object %s is %d' %(obj, sfo.status))
            return None

        dfmt = sfo.dataFormat
        addr = sfo.address
        bytlen = sfo.length
        SFOlbl = sfo.SFOtypeLabel

        if tbeg is not None or tend is not None:
            if tend is None:
                tend = 10.
            if tbeg is None:
                tbeg = 0.
            tb = self.gettimebase(obj)
            if tb is None: # AB with no time dependence
                logger.warning('%s has no Timebase associated, returning full array', obj)
                sfo.getData()
                return sfo.data
            jt_beg, jt_end = tb.searchsorted((tbeg, tend))
            if SFOlbl == 'TimeBase':
                return tb[jt_beg: jt_end]
            elif SFOlbl in ('Signal', 'AreaBase') or self.time_last(obj):
                sfo.getData(nbeg=jt_beg, nend=jt_end)
                return self.getobject(obj, cal=cal, nbeg=jt_beg, nend=jt_end)
            elif self.time_first(obj):
                return self.getobject(obj, cal=cal)[jt_beg: jt_end]
            else:
                logger.error('Object %s: tbeg, tend keywords supported only when time is first or last dim', obj)
                return None
        else:
            sfo.getData(nbeg=nbeg, nend=nend)

        data = sfo.data

# LongLong in [ns] and no zero at TS06
        if SFOlbl == 'TimeBase' and sfo.dataFormat == LONGLONG and cal: # RMC:TIME-AD0, SXS:Time
            logger.debug('Before getts06 dfmt:%d addr:%d len:%d data1:%d, %d', dfmt, addr, bytlen, data[0], data[1])
            data = 1e-9*(data - self.getts06(obj))
            logger.debug('%d',  self.getts06(obj))

        dout = sfobj.SFOBJ(data, sfho=sfo) # Add metadata
        dout.calib = False
# Calibrated signals and signal groups
        if SFOlbl in ('SignalGroup', 'Signal'):
            if cal:
                dout = self.raw2calib(dout)
                if self.diag in ('DCN', 'DCK', 'DCR'):
                    dout.phys_unit = '1/m^2'

        return dout


    def lincalib(self, sfo):
        """
        Returns coefficients for signal(group) calibration
        """

        for robj in sfo.relobjects:
            if robj.SFOtypeLabel == 'ParamSet':
                caltyp = robj.cal_type
                logger.debug('PSet for calib: %s, cal type: %d', robj.objectName, caltyp)
                if caltyp == sfmap.calibType['LinCalib']:
                    return self.getparset(robj.objectName)
                elif caltyp == sfmap.calibType['extCalib']:
                    diag_ext = ''.join(robj.data['DIAGNAME'].data)
                    shot_ext = libddc.previousshot(diag_ext, shot=self.shot)
                    ext = read_other_sf(shot_ext, diag_ext)
                    return ext.getparset(robj.objectName)
        return None


    def raw2calib(self, sfo):
        """
        Calibrates an uncalibrated Signal or SignalGroup
        """
# Calibrated signals and signal groups
        if sfo.SFOtypeLabel not in ('SignalGroup', 'Signal'):
            logging.error('Calibration failed for %s: no Sig, no SGR', sfo.objectname)
            return sfo

        pscal = self.lincalib(sfo)
        if pscal is None:
            if sfo.phys_unit == 'counts':
                for robj in sfo.relobjects:
                    if robj.SFOtypeLabel == 'TimeBase':
                        return robj.s_rate*np.float32(sfo)
            return sfo

        for j in range(10):
            mult = 'MULTIA0%d' %j
            shif = 'SHIFTB0%d' %j
            if not mult in pscal.keys():
                break
# we need to fix the content of pscal for signagroups
# assuming first entry wins
            if j == 0:
                sfo = sfo *1. # Creates a copy of a read-only array, only once
                sfo.calib = True
            multi = np.atleast_1d(pscal[mult])
            shift = np.atleast_1d(pscal[shif])
            if sfo.SFOtypeLabel == 'Signal' or len(multi) == 1:
                sfo *= multi[0] # MXR
                sfo += shift[0]
            else:
                n_pars = sfo.shape[1]
                if n_pars != len(multi):
                    logger.warning('Inconsitent sizes in calibration PSet %s', obj)
                if n_pars <= len(multi):
                    sfo *= multi[: n_pars] # BLB
                    sfo += shift[: n_pars]
                else:
                    sfo *= multi[0]
                    sfo += shift[0]

        return sfov


    def getparset(self, pset):
        """
        Returns data and metadata of a Parameter Set
        """

        pset = str_byt.to_str(pset)
        sfo = self.sf[pset]
        if sfo.SFOtypeLabel not in ('Device', 'ParamSet'):
            return None

        pset_d = {}

        for pname, param in sfo.data.items():
            pset_d[pname] = sfobj.SFOBJ(param.data, sfho=param)
#
#        logger.debug('PSET %s, oytp %s', pset, sfo.SFOtypeLabel)
        return pset_d


    def getlist(self, obj=None):
        """
        Returns a list of data-objects of a shotfile
        """
        if obj is None:
            obj = 'SIGNALS'
        else:
            obj = str_byt.to_str(obj)

        return self.sf[obj].data


    def getlist_by_type(self, SFOlbl='Signal'):
        """
        Returns a list of names of all SF-objects of a given type (Signal, TimeBase)
        """
        return [lbl for lbl, sfo in self.sf.items() if sfo.SFOtypeLabel == SFOlbl]


    def getobjectName(self, jobj):
        """
        Returns the object name for an inpur object ID
        """

        for lbl, sfo in self.sf.items():
            if sfo.objid == jobj:
                return lbl


    def getdevice(self, lbl):
        """
        Returns a DEVICE object
        """

        return self.sf[lbl].data


    def get_ts06(self):
# Look anywhere in the diagsnostic's Devices
        ts06 = None
        for sfo in self.sf.SFobjects:
            if sfo.SFOtypeLabel == 'Device':
                ps = sfo.data
                if 'TS06' in ps.keys():
                    ts6 = ps['TS06'].data
                    if ts6 > 1e15:
                        ts06 = ts6
                        break
        return ts06


    def getts06(self, obj):
        """
        Reads the diagnostic internal TS06 from parameter set
        """
        ts06 = None
        if self.sf[obj].SFOtypeLabel == 'TimeBase':
            tb = obj
        else:
            for rel_obj in self.sf[obj].relations:
                if self.sf[rel_obj].SFOtypeLabel == 'TimeBase': # related TB
                    tb = rel_obj
                    break
        if 'tb' in locals(): # No TB related
            obj2 = tb
        else: # try a direct relation
            obj2 = obj

        for rel_obj in self.sf[obj2].relations:
            if self.sf[rel_obj].SFOtypeLabel == 'Device': # related device
                ps = self.sf[rel_obj].data
                if 'TS06' in ps.keys():
                    ts6 = ps['TS06'].data
                    if ts6 > 1e15:
                        ts06 = ts6
                        break

        logger.debug('getts06 %s %d', rel_obj, ts06)
        if ts06 is None:
            ts06 = self.get_ts06()
        if ts06 is None:
            ts06 = getcti_ts06(self.shot)
        return ts06


    def time_first(self, obj):
        """
        Tells whether a SigGroup has time as first coordinate
        by comparing with the size of the related TBase
        """

        obj = str_byt.to_str(obj)
        sfo = self.sf[obj]
        if sfo.SFOtypeLabel != 'SignalGroup':
            return False
        else:
            return (sfo.time_dim == 0)


    def time_last(self, obj):
        """
        Tells whether a SigGroup has time as first coordinate
        by comparing with the size of the related TBase
        """

        obj = str_byt.to_str(obj)
        sfo = self.sf[obj]
        if sfo.SFOtypeLabel != 'SignalGroup':
            return False
        else:
            return (sfo.time_dim == sfo.num_dims-1)
