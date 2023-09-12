import os, logging, traceback, time
import time
from struct import unpack, pack
import numpy as np
from aug_sfutils import sfmap, str_byt
from aug_sfutils.sfmap import oid, olbl, ostruc, oattr, header_sfmt

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')

logger = logging.getLogger('aug_sfutils.shotfile')

if len(logger.handlers) == 0:
    hnd = logging.StreamHandler()
    hnd.setFormatter(fmt)
    logger.addHandler(hnd)

logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

PPGCLOCK = [1e-6, 1e-5, 1e-4, 1e-3]
LOGICAL  = sfmap.typeMap('descr', 'SFfmt', 'LOGICAL')


def getChunk(fname, start, length):
    """Reads the requested byteblock from the binary shotfile"""

    rdata = None
    with open(fname, 'rb') as f:
        f.seek(start)
        rdata = f.read(length)
    return rdata


def next8(bytlen):
    return 8 * ( (bytlen + 7)//8 )


def param_length(param):
    """Determines the byte length of a Parameter"""

    dfmt = param.dataFormat
    bytlen = param.n_items * sfmap.typeLength(dfmt)

    return 16 + 8 * ( (bytlen + 13)//8 )


def parset_length(pset_d):
    """Determines the byte length of a ParameterSet"""

    psetlen = 0
    for lbl, param in pset_d.items():
        param.objectName = lbl
        param.setDefault()
        psetlen += param_length(param)

    return psetlen


def par2byt(pname, param):
    """Converts the parameter data into bytes"""

    dfmt = param.dataFormat
    n_items = param.n_items

    if dfmt in sfmap.fmt2len.keys(): # char variable
        dlen = sfmap.fmt2len[dfmt]
        bytlen = n_items * dlen + 2
    elif dfmt in sfmap.dtf['SFfmt'].values: # number
        sfmt = sfmap.typeMap('SFfmt', 'struc', dfmt)
        type_len = np.dtype(sfmt).itemsize
        val_len = n_items + 2
        bytlen = val_len * type_len
    dj0 = next8(bytlen)
    blen = 16 + dj0
    byt = bytearray(blen)
    byt[  :  8] = str_byt.to_byt(pname.ljust(8))
    byt[ 8: 16] = pack('>4h', param.physunit, dfmt, n_items, param.status)
    if dfmt in sfmap.fmt2len.keys(): # character variable
        byt[16: 17] = param.dmin
        byt[17: 18] = param.dmax
        param2 = np.atleast_1d(param.data)
        for jitem in range(n_items):
            if len(param2[jitem]) > 0:
                byt[18 + jitem*dlen: 18 + (jitem+1)*dlen] = str_byt.to_byt(param2[jitem]).ljust(dlen)
    elif dfmt in sfmap.dtf['SFfmt'].values: # number
        if dfmt == LOGICAL: # logical, bug if n_items > 1?
            byt[16: 22] = pack('>?2x?1x?', param.dmin, param.dmax, param)
        else:
            byt[16: 16+2*type_len] = pack('>2%s' %sfmt, param.dmin, param.dmax)
            param2 = np.atleast_1d(param.data)
            byt[16: 16 + (n_items+2)*type_len] = pack('>%d%s' %(2+n_items, sfmt), param.dmin, param.dmax, *param2)
    return byt


class SHOTFILE(dict):


    def __init__(self, sfpath, sffull=None):

        self.__dict__ = self

        if not os.path.isfile(sfpath) and sffull is None:
            logger.error('Shotfile %s not found', sfpath)
            return None

        if sffull is None: # read shotfile if no SFobj is input
            self.shotfilePath = sfpath
            self.read_sfh()
            self.set_attributes()
        else: # for SF writing
            if isinstance(sffull, dict):
                for key, val in sffull.items():
                    setattr(self, key, val)
            else:
                for key, val in sffull.__dict__.items():
                    setattr(self, key, val)
            self.shotfilePath = sfpath
            self.sfh2byte() # converts to bytes string (Shotfile content)


    def read_sfh(self, psets=True):
        """Reads a full shotfile header, including the data of ParamSets, Devices, Lists"""

        self.SFobjects = []
        self.addressMultiplier   = 1

        n_max = 1000
        n_obj = n_max
        self.objId2objName = []
        for j in range(n_max):
            sfo = SF_OBJECT(jobj=j, sfname=self.shotfilePath)
            if hasattr(sfo, 'objectType'):
                sfo.objid = j
                onam = sfo.objectName
                if sfo.SFOtypeLabel == 'Diagnostic':
                    if n_obj == n_max: # There might be several diags objects in a SFH
                        self.shotNumber = sfo.shot
                        self.diagName   = str_byt.to_str(sfo.diag.strip())
                        n_obj = sfo.num_objs
                self.objId2objName.append(onam)
                self.SFobjects.append(sfo)
                if sfo.SFOtypeLabel == 'ADDRLEN':
                    self.addressMultiplier = sfmap.addrsizes[sfo.addrlen]
                self.__dict__[onam] = sfo
            if j >= n_obj - 1:
                break


    def set_attributes(self):
        """Sets useful context info for the entire shotfile, plus data for Lists, ParmSets, Devices"""

        for sfo in self.SFobjects:
            sfo.address *= self.addressMultiplier
            sfo.relations  = [self.objId2objName[jid] for jid in sfo.rel if jid != 65535]
            sfo.relobjects = [self.SFobjects[jid]     for jid in sfo.rel if jid != 65535]
            if hasattr(sfo, 'dataFormat'):
                if sfo.dataFormat in sfmap.dtf['SFfmt'].values:
                    sfo.dataType = sfmap.typeMap('SFfmt', 'descr', sfo.dataFormat)

            if sfo.SFOtypeLabel == 'List':
                sfo.getList()
                sfo.data = [self.objId2objName[jid] for jid in sfo.data]
            elif sfo.SFOtypeLabel in ('Device', 'ParamSet'):
                sfo.getParamSet()
            elif sfo.SFOtypeLabel in ('Signal', 'SignalGroup'):
                for jrel, robj in enumerate(sfo.relobjects):
# check where the related timebase is
                    if robj.SFOtypeLabel == 'TimeBase':
                        shape_arr = sfo.index[::-1][:sfo.num_dims]
                        nt = robj.n_steps
                        if shape_arr.count(nt) == 1:
                            sfo.time_dim = shape_arr.index(nt)
                        sfo.timebase = robj
                        sfo.time_dim = jrel
# For data calibration
                        if sfo.phys_unit == 'counts':
                            sfo.cal_fac = robj.s_rate
# check where the related areabase is
                    elif robj.SFOtypeLabel == 'AreaBase':
                        sfo.areabase = robj
                        sfo.area_dim = jrel

#----------------
# Writing section
#----------------
    def sfh2byte(self):
        """Converts all SF objects' metadata to bytes (shotfile header content)"""

# Fill missing attributes in signle objects

        if not hasattr(self, 'SFobjects'):
            self.SFobjects = []
            for lbl, sfo in vars(self).items():
                if hasattr(sfo, 'data') or hasattr(sfo, 'SFOtypeLabel'):
                    sfo.objectName = lbl
                    sfo.setDefault()
                    self.SFobjects.append(sfo)

        self.setSIGNALS()
        objNames = [sfo.objectName for sfo in self.SFobjects]
        if 'SIGNALS' not in objNames:
            self.SFobjects.insert(1, self.SIGNALS)
        self.setSIGNALSdata()

        objName2objId = {}
        for jid, sfo in enumerate(self.SFobjects):
            objName2objId[sfo.objectName] = jid

        for jid, sfo in enumerate(self.SFobjects):
            if not hasattr(sfo, 'rel'):
                if hasattr(sfo, 'relations'):
                    sfo.rel = [objName2objId[oname] for oname in sfo.relations]
                    if len(sfo.rel) < 8:
                        sfo.rel += (8-len(sfo.rel))*[65535] # Filling with no-rel
                else:
                    sfo.rel = 8*[65535] # defaulting to "no relations"

        self.set_length_address()

        num_objs = len(self.SFobjects)
        self.SFbytes = b''
        for sfo in self.SFobjects:
            if sfo.SFOtypeLabel == 'Diagnostic':
                sfo.num_objs = num_objs
# Encode all attributes into byte strings(128)
            self.SFbytes += sfo.sfoh2byte()

# Write SIGNALS list
        self.SFbytes += self.SIGNALS.data

# Write content of ParSets
        for sfo in self.SFobjects:
            if sfo.SFOtypeLabel == 'ParamSet':
                pset2byt = b''
                for pname, param in sfo.data.items():
                    pset2byt += par2byt(pname, param)
                self.SFbytes.ljust(sfo.address) # Ensure proper localisation
                self.SFbytes += pset2byt


    def putData(self):
        """Add data to Sf objects"""

        for sfo in self.SFobjects:
            if sfo.SFOtypeLabel in sfmap.DataObjects:
                if hasattr(sfo, 'data'):
                    sfmt  = sfmap.typeMap('SFfmt', 'struc', sfo.dataFormat)
                    sfo.data = sfo.data.astype('>%s' %sfmt)
                    if sfo.data.nbytes == sfo.length:
                        self.SFbytes = self.SFbytes.ljust(sfo.address)
                        self.SFbytes += sfo.data.tobytes(order='F')
                    else:
                        logger.error('Shape/type of %s does not match buffer length', sfo.objectName)
                        return
                else:
                    logger.warning('Missing data for object %s', sfo.objectName)


    def dumpShotfile(self):
        """Dumps Shotfile(header)"""

        sfout = self.shotfilePath
        if hasattr(self, 'SFbytes'):
            with open(sfout, 'wb') as f:
                f.write(self.SFbytes)
            logger.info('Stored binary %s' %sfout)


    def setSIGNALS(self):
        """Generates 'SIGNALS' list automatically"""

# SIGNALS list generated automatically, override input entry
        self.SIGNALS = SF_OBJECT()
        self.SIGNALS.dataFormat = sfmap.typeMap('descr', 'SFfmt', 'SHORT_INT')
        self.SIGNALS.SFOtypeLabel = 'List'
        self.SIGNALS.objectName = 'SIGNALS'


    def setSIGNALSdata(self):

        sfmt = sfmap.typeMap('SFfmt', 'struc', self.SIGNALS.dataFormat)
        objid = [jid for jid, sfo in enumerate(self.SFobjects) if sfo.SFOtypeLabel in sfmap.DataObjects]
        self.SIGNALS.nitems = len(objid)
        self.SIGNALS.data = pack('>%d%s' %(self.SIGNALS.nitems, sfmt), *objid)
        self.SIGNALS.length = len(self.SIGNALS.data)
        self.SIGNALS.address = len(self.SFobjects)*128
        self.SIGNALS.setDefault()


    def set_length_address(self):
        """Recalculates the address and length of SF objects, recreating the 'SIGNALS' list consistently"""

# ParSets

        len_psets = 0
        for jid, sfo in enumerate(self.SFobjects): # sequence not important
            if sfo.SFOtypeLabel == 'ParamSet':
                sfo.length = parset_length(sfo.data)
                len_psets += sfo.length

# Set lengths and addresses

        addr_diag = self.SIGNALS.address + self.SIGNALS.length + len_psets
        par_addr  = self.SIGNALS.address + self.SIGNALS.length

        addr = addr_diag

        for sfo in self.SFobjects:
            SFOlbl = sfo.SFOtypeLabel
            if hasattr(sfo, 'dataFormat'):
                type_len = sfmap.typeLength(sfo.dataFormat)
            else:
                type_len = 0

            if SFOlbl == 'Diagnostic':
                sfodiag = sfo
                sfo.address = addr
            elif SFOlbl == 'List':
                if sfo.objectName == 'SIGNALS':
                    for key, val in self.SIGNALS.__dict__.items():
                        setattr(sfo, key, val)
                    addr = addr_diag
            elif SFOlbl in ('Device', 'ParamSet'):
                sfo.address = par_addr
                par_addr += sfo.length
            elif SFOlbl in sfmap.DataObjects:
                sfo.length = sfmap.objectLength(sfo)
                sfo.address = addr
                addr += sfo.length
            else:
                continue

        sfodiag.length = addr + sfo.length + addr_diag



class SF_OBJECT:
    """Reads/writes the metadata of a generic single object (sfo) of a Shotfile from/to the SFH's 128byte string.
    To fetch the corresponding data, call getData()"""


    def __init__(self, jobj=None, sfname=None):


        if sfname is not None:
            self.sfname = sfname
            self.read_sfoh(jobj)


    def read_sfoh(self, jobj):

        byte_str = getChunk(self.sfname, jobj*128, 128)

        objnam, self.objectType, self.level, self.status, self.errcode, *rel, \
            self.address, self.length, val, descr = unpack(header_sfmt, byte_str)

        self.objectName = str_byt.to_str(objnam).strip()
        if not self.objectName:
            logger.error('Error: empty object name')
            return
        self.rel = list(rel)
        self.descr = str_byt.to_str(descr.strip())

        logger.debug('%s %d %d', self.objectName, self.address, self.length)
        logger.debug(self.descr)

        if self.objectType in olbl.keys():
            self.SFOtypeLabel = olbl[self.objectType]
            sfmt = ostruc[self.SFOtypeLabel]
        else:
            sfmt = None
            self.SFOtypeLabel = 'Unknown'

# Read SFheader, plus data for Lists, Devices, ParSets
        SFOlbl = self.SFOtypeLabel
        SFOtup = unpack(sfmt, val)
        for jattr, SFOattr in enumerate(oattr[SFOlbl]):
            setattr(self, SFOattr, SFOtup[jattr])

        if SFOlbl == 'ParamSet':
            self.calibration_type = sfmap.calibLabel[self.cal_type]
        elif SFOlbl in ('SignalGroup', 'Signal'):
            self.index = [self.index1, self.index2, self.index3, self.index4]
            if self.physunit in sfmap.unitLabel.keys():
                self.phys_unit = sfmap.unitLabel[self.physunit]
            else:
                logger.warning('No phys. unit found for object %s, key=%d', self.objectName, self.physunit)
                self.phys_unit = ''
        elif SFOlbl == 'TimeBase':
            self.timebase_type = sfmap.tbaseLabel[self.tbase_type]
        elif SFOlbl == 'AreaBase':
            self.physunit = [self.physunit1, self.physunit2, self.physunit3]
            self.phys_unit = [sfmap.unitLabel[x] for x in self.physunit]
            self.sizes = [self.size_x, self.size_y, self.size_z]


    def getData(self, nbeg=0, nend=None):
        """Stores the data part of a SF object into sfo.data"""

        if self.SFOtypeLabel in ('ParamSet', 'Device'):
            self.getParamSet()
        elif self.SFOtypeLabel == 'List':
            self.getList()
        elif self.SFOtypeLabel == 'SFList':
            self.getSFList()
        elif self.SFOtypeLabel in sfmap.DataObjects:
            self.getObject(nbeg=nbeg, nend=nend)


    def getList(self):
        """Stores the object IDs contained in a SF list (such as SIGNALS)"""

        sfmt = sfmap.typeMap('SFfmt', 'struc', self.dataFormat)
        self.data = np.ndarray((self.nitems, ), '>%s' %sfmt, getChunk(self.sfname, self.address, self.length), order='F') # IDs, not labels


    def getSFList(self):
        """Stores the object IDs contained in a SF list (such as SIGNALS)"""

        self.depth = []
        self.exp   = []
        self.diag  = []
        self.sshot = []
        self.level = []
        self.ed    = []
        self.date  = []
        len_str = 44
        buf = getChunk(self.sfname, self.address, self.nitems*len_str)
        for jitem in range(self.nitems):
            depth1, exp1, diag1, sshot1, diag2, ed1, lbl, date1 = unpack('>h8s3s5s8sh8sI4x', buf[len_str*jitem: len_str*(jitem+1)])
            self.depth.append(depth1)
            self.exp.append( str_byt.to_str(exp1))
            self.diag.append(str_byt.to_str(diag1))
            self.sshot.append(str_byt.to_str(sshot1))
            self.ed.append(ed1)
            self.date.append(time.ctime(date1))


    def getParamSet(self):
        """Returns data and metadata of a Parameter Set.
        Called by default on SFH reading"""

        buf = getChunk(self.sfname, self.address, self.length)

        j0 = 0
        self.data = {}
        logger.debug('PS: %s, addr: %d, n_item: %d, length: %d', self.objectName, self.address, self.nitems, self.length)
        for j in range(self.nitems):
            param = SF_OBJECT()
            param.SFOtypeLabel = 'Parameter'
            pnameb, param.physunit, dfmt, n_items, param.status = unpack('>8s4h', buf[j0:  j0+16])
            param.objectName = str_byt.to_str(pnameb).strip()
            if param.physunit in sfmap.unitLabel.keys():
                param.phys_unit = sfmap.unitLabel[param.physunit]
            else:
                param.phys_unit = ''
            param.n_items = n_items
            param.dataFormat = dfmt

            j0 += 16

            if dfmt in sfmap.fmt2len.keys(): # char variable
                dlen = sfmap.fmt2len[dfmt]
                bytlen = n_items * dlen + 2
                param.dmin = buf[j0  : j0+1]
                param.dmax = buf[j0+1: j0+2]
                if not param.dmin:
                    param.dmin = ' '
                if not param.dmax:
                    param.dmax = ' '
                param2 = np.chararray((n_items,), itemsize=dlen, buffer=buf[j0+2: j0+bytlen])
                param.data = list(map(str_byt.to_str, param2))
            elif dfmt in sfmap.dtf['SFfmt'].values:
                sfmt = sfmap.typeMap('SFfmt', 'struc', dfmt)
                logger.debug('Numerical par %d', dfmt)
                val_len = n_items + 2
                bytlen = val_len * np.dtype(sfmt).itemsize
                if n_items >= 0:
                    if dfmt == LOGICAL: # Logical, bug if n_items > 1?
                        param.dmin, param.dmax, param.data = unpack('>?2x?1x?', buf[j0: j0+6])
                    else:
                        data = np.ndarray((val_len, ), '>%s' %sfmt, buf[j0: j0+bytlen], order='F').copy()
                        param.dmin = data[0]
                        param.dmax = data[1]
                        param.data = np.squeeze(data[2:]) # no array if n_items=1
            else: # faulty dfmt
                break
            dj0 = next8(bytlen)
            j0 += dj0

            self.data[param.objectName] = param

            if j0 >= self.length:
                break


    def getObject(self, nbeg=0, nend=None):
        """Reads data part of Sig, SigGrou, TimeBase, AreaBase"""

        if hasattr(self, 'nbeg'):
           if self.nbeg == nbeg and self.nend == nend:
               return # do not re-read object if data are there already
        self.nbeg = nbeg
        self.nend = nend
        if self.SFOtypeLabel in sfmap.DataObjects:
            shape_arr = sfmap.arrayShape(self)
        else:
            logger.error('Object %s is no signal, signalgroup, timebase nor areabase, skipping')
            return None

        dfmt = self.dataFormat
        if self.SFOtypeLabel == 'TimeBase' and self.length == 0:
            if self.tbase_type == sfmap.tbaseType['PPG_prog']: # e.g. END:T-LM_END
                self.ppg_time()
            else:   # ADC_intern, e.g. DCN:T-ADC-SL
                self.data = (np.arange(self.n_steps, dtype=np.float32) - self.n_pre)/self.s_rate
        else:
            type_len = sfmap.typeLength(dfmt)
            bytlen = np.prod(shape_arr) * type_len
            if dfmt in sfmap.fmt2len.keys(): # char variable
                data2 = np.chararray(shape_arr, itemsize=type_len, buffer=getChunk(self.sfname, self.address, bytlen), order='F')
                self.data = np.array([str_byt.to_str(val) for val in data2.ravel()]).reshape(data2.shape) # <1ms for SSQ
            else: # numerical variable
                sfmt = sfmap.typeMap('SFfmt', 'struc', dfmt)
                addr = self.address
# Read data only in the time range of interest
                if self.SFOtypeLabel in ('Signal', 'TimeBase', 'AreaBase') or self.time_last():
                    addr += type_len*nbeg*np.prod(shape_arr[:-1])
                    if nend is None:
                        nend = shape_arr[-1]
                    bytlen = (nend - nbeg)*np.prod(shape_arr[:-1])*type_len
                    shape_arr[-1] = nend - nbeg
                self.data = np.memmap(self.sfname, dtype='>%s' %sfmt, mode='r', offset=addr, shape=tuple(shape_arr), order='F')


    def ppg_time(self): # Bug MAG:27204; e.g. END
        """Returns the time-array in [s] for TB of type PPG_prog"""

        nptyp = sfmap.typeMap('SFfmt', 'np', self.dataFormat)
        for robj in self.relobjects:
            if robj.SFOtypeLabel == 'Device':
                ppg = robj.data # Device/ParSet dictionary
                if not 'PRETRIG' in ppg.keys():
                    continue
                if self.n_pre > 0:
                    if ppg['PRETRIG'].data > 0:
                        dt = ppg['RESOLUT'].data[15] * PPGCLOCK[ppg['RESFACT'].data[15]] + 1e-6
                    else:
                        dt = 0.
                    time_ppg = dt*np.arange(self.n_pre, dtype=nptyp) - dt*self.n_pre
                    start_phase = time_ppg[-1] + dt
                else:
                    time_ppg = []
                    start_phase = 0
                for jphase in range(16):
                    if ppg['PULSES'].data[jphase] > 0:
                        dt = ppg['RESOLUT'].data[jphase]*PPGCLOCK[ppg['RESFACT'].data[jphase]]
                        tb_phase = dt*np.arange(ppg['PULSES'].data[jphase], dtype=nptyp) + start_phase
                        time_ppg = np.append(time_ppg, tb_phase)
                        start_phase = time_ppg[-1] + dt
                if len(time_ppg) != 0:
                    self.data = time_ppg[:self.n_steps]


    def time_last(self):
        """True if SigGroup has time as last coordinate"""

        if not hasattr(self, 'time_dim'):
            return False
        else:
            return (self.time_dim == self.num_dims-1)


    def sfoh2byte(self):
        """Converts SF object attributes into a 128bytes header string"""

# val string
        SFOlbl = self.SFOtypeLabel
        sfmt = ostruc[SFOlbl]

        descr      = str_byt.to_byt(self.descr)
        objectName = str_byt.to_byt(self.objectName)

        valList = []
        for SFOattr in sfmap.oattr[SFOlbl]:
            if hasattr(self, SFOattr):
                valList.append(getattr(self, SFOattr))
            else:
# String attributes
                if SFOattr in ('diag', 'hostname', 'date'):   # only for Algorithm
                    valList.append(b'')
# (Various) integer types
                else:
                    valList.append(0)
        val = pack(sfmt, *valList)

# Pack all SFh attributes
        sfoh_byte = pack(header_sfmt, objectName.ljust(8), self.objectType, \
            self.level, self.status, self.errcode, *self.rel, self.address, \
            self.length, val, descr.ljust(64))

        return sfoh_byte


    def setDefault(self):
        """Defaulting missing attributes whenever possible"""

        if not hasattr(self, 'objectName'):
            logger.error('Missing attribute objectName')
            return

# Some defaults in case of missing attributes

        type_err = 'SF object type not understood'
        if not hasattr(self, 'SFOtypeLabel'):
            if hasattr(self, 'objectType'):
                self.SFOtypeLabel = olbl[self.objectType]
            else:
                if not hasattr(self, 'data'):
                    logger.error(type_err)
                    return
                if hasattr(self.data, 'ndim'):
                    if self.data.ndim == 1:
                        self.SFOtypeLabel = 'Signal'      # default: Signal for 1D arrays
                    elif self.data.ndim > 1:
                        self.SFOtypeLabel = 'SignalGroup' # default: SignalGroup for 2-3D arrays
                    else:
                        logger.error(type_err)
                        return

        if not hasattr(self, 'objectType'):
            self.objectType = oid[self.SFOtypeLabel]

        if self.SFOtypeLabel == 'Parameter':
            if not hasattr(self, 'n_items'):
                self.n_items = len(self.data)
            if not hasattr(self, 'physunit'):
                if hasattr(self, 'phys_unit'):
                    self.physunit = sfmap.unitType[self.phys_unit]
                elif hasattr(self, 'unit'):
                    self.physunit = sfmap.unitType[self.unit]
                else:
                    self.physunit = 0
            if not hasattr(self, 'dmin'):
                self.dmin = self.data.min()
            if not hasattr(self, 'dmax'):
                self.dmax = self.data.max()
        elif self.SFOtypeLabel == 'ParamSet':
            if not hasattr(self, 'nitems'):
                self.nitems = len(self.data)
            if not hasattr(self, 'cal_type'):
                if hasattr(self, 'calibration_type'):
                    self.cal_type = sfmap.calibType[self.calibration_type]
                else:
                    self.cal_type = 0
        elif self.SFOtypeLabel == 'Diagnostic':
            self.diag    = str_byt.to_byt(self.objectName).ljust(4)
            self.version = 4
            self.c_time  = int(time.time())
            if not hasattr(self, 'exp'):
                self.exp       = sfmap.expType['PRIV']
            if not hasattr(self, 'diag_type'):
                self.diag_type = sfmap.diagType['DataAcqu']
            if not hasattr(self, 'up_limit'):
                self.up_limit  = 256
            if not hasattr(self, 's_type'):
                self.s_type = sfmap.shotType['NormalShot']
        elif self.SFOtypeLabel == 'TimeBase':
            self.n_steps = len(self.data)
        elif self.SFOtypeLabel == 'AreaBase':
            ashape = self.data.shape
            adim = self.data.ndim
            self.size_y = 0
            self.size_z = 0
            if adim == 1:
                self.size_x = ashape[0]
            elif adim == 2:
                self.size_x, self.size_y = ashape
            elif adim == 3:
                self.size_x, self.size_y, self.size_z = ashape
            if not hasattr(self, 'n_steps'):
                self.n_steps = 1
        elif self.SFOtypeLabel in ('Signal', 'SignalGroup'):
            self.num_dims = self.data.ndim
            self.index4 = self.data.shape[0]
            if self.data.ndim > 1:
                self.index3 = self.data.shape[1]
            else:
                self.index3 = 1
            if self.data.ndim > 2:
                self.index2 = self.data.shape[2]
            else:
                self.index2 = 1
            if self.data.ndim > 3:
                self.index1 = self.data.shape[3]
            else:
                self.index1 = 1
            self.index = [self.index1, self.index2, self.index3, self.index4]
            if not hasattr(self, 'physunit'):
                if hasattr(self, 'phys_unit'):
                    self.physunit = sfmap.unitType[self.phys_unit]
                elif hasattr(self, 'unit'):
                    self.physunit = sfmap.unitType[self.unit]
                else:
                    self.physunit = 0

        if self.SFOtypeLabel in sfmap.DataObjects or self.SFOtypeLabel == 'Parameter':
            if not hasattr(self, 'dataFormat'):
                if hasattr(self, 'data'):
                    self.dataFormat = sfmap.typeMap('np', 'SFfmt', self.data.dtype)
                else:
                    logger.error('Missing dataFormat for object %s', self.objectName)
                    return

        if not hasattr(self, 'descr'):
            self.descr = b''

        for attr in ('level', 'status', 'errcode'):
            if not hasattr(self, attr):
                setattr(self, attr, 0)
