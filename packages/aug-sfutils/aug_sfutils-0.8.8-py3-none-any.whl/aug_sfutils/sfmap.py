"""Definitions of object and data types, units, 
calibration types, timebase types.
"""

import numpy as np
import ctypes as ct
import pandas as pd

#  SFfmt, SFtyp,       np,         ct, struc,   descr
dtypesList = [ \
  [  1,   0,    np.int8,   ct.c_byte, 'b', 'BYTE'        ],
  [  2,   6,        str,   ct.c_char, 'c', 'CHAR'        ],
  [  3,  11,   np.int16,  ct.c_int16, 'h', 'SHORT_INT'   ],
  [  4,   1,   np.int32,  ct.c_int32, 'i', 'INTEGER'     ],
  [  5,   2, np.float32,  ct.c_float, 'f', 'IEEE_FLOAT'  ],
  [  6,   3, np.float64, ct.c_double, 'd', 'IEEE_DOUBLE' ],
  [  7,   5,       bool,   ct.c_bool, '?', 'LOGICAL'     ],
#  [  8,  -1,       None,        None,  '', 'CHAR_REAL'   ],
  [  9,  12,  np.uint16, ct.c_uint16, 'H', 'U_SHORT'     ],
#  [ 10,  -1,       None,        None,  '', 'IBM_REAL'    ], 
#  [ 11,  -1,       None,        None,  '', 'IBM_DOUBLE'  ], 
#  [ 12,  -1,       None,        None,  '', 'CONDENSED_TB'], 
  [ 13,  10,   np.int64,  ct.c_int64, 'q', 'LONGLONG'    ],
  [ 14,  13,  np.uint32, ct.c_uint32, 'I', 'U_INTEGER'   ],
  [ 15,  14,  np.uint64, ct.c_uint64, 'Q', 'U_LONGLONG'  ],
]

dtf = pd.DataFrame(dtypesList, columns = ['SFfmt', 'SFtyp', 'np', 'ct', 'struc', 'descr'])


SFOtypeList = [\
    [ 1, 'Diagnostic' , '>4s2H2I4H' , ('diag', 'num_objs', 'diag_type', 'shot', 'c_time', 'up_limit', 'exp', 'version', 's_type')],
    [ 2, 'List'       , '>4H16x'    , ('dataFormat', 'nitems', 'ordering', 'list_type')],
    [ 3, 'Device'     , '>4H2I2HI'  , ('dataFormat', 'acquseq', 'nitems', 'dev_type', 'dev_addr', 'n_chan', 'task', 'dev_num', 'n_steps')],
    [ 4, 'ParamSet'   , '>4x2H16x'  , ('nitems', 'cal_type')],
    [ 5, 'MapFunc'    , '>4x2H8xH6x', ('nitems', 'map_type', 'task')],
    [ 6, 'SignalGroup', '>3Hh4I'    , ('dataFormat', 'physunit', 'num_dims', 'stat_ext', 'index1', 'index2', 'index3', 'index4')],
    [ 7, 'Signal'     , '>3Hh4I'    , ('dataFormat', 'physunit', 'num_dims', 'stat_ext', 'index1', 'index2', 'index3', 'index4')],
    [ 8, 'TimeBase'   , '>4HI4x2I'  , ('dataFormat', 'burstcount', 'event', 'tbase_type', 's_rate', 'n_pre', 'n_steps')],
    [ 9, 'SFList'     , '>2xH20x'   , ('nitems', )],
    [10, 'Algorithm'  , '>8x8s8s'   , ('hostname', 'date')],
    [11, 'UpdateSet'  , '>2xHi8x2I' , ('nitems', 'input_vals', 'next_index', 'size')],
    [12, 'LocTimer'   , '>2H16xI'   , ('dataFormat', 'resolution', 'size')],
    [13, 'AreaBase'   , '>4H4I'     , ('dataFormat', 'physunit1', 'physunit2', 'physunit3', 'size_x', 'size_y', 'size_z', 'n_steps')],
    [14, 'Qualifier'  , '>H2x2H4I'  , ('dataFormat', 'num_dims', 'qsub_typ', 'index_4', 'index_3', 'index_2', 'max_sections')],
    [15, 'ModObj'     , '>H22x'     , ('nitems', )],
    [16, 'MapExtd'    , '>2H2I2H2I' , ('nitems', 'mapalg', 'tbeg', 'tend', 'val_0', 'val_1', 'val_2', 'val_3')],
    [17, 'Resource'   , '>2H20x'    , ('num_cpus', 'first_cpu')],
    [18, 'ADDRLEN'    , '>H22x'     , ('addrlen', )] ]

sfof = pd.DataFrame(SFOtypeList, columns = ['SFOtypeID', 'SFOtypeLabel', 'SFOtypeStruc', 'SFOattrs'])

header_sfmt = '>8s3Hh8H2I24s64s'

DataObjects = ('Signal', 'SignalGroup', 'TimeBase', 'AreaBase')

def dict_inv(dict_in):
    return {val: key for key, val in dict_in.items()}

# CHAR length for string variables
fmt2len = {2: 1, 1794: 8, 3842: 16, 7938: 32, 12034: 48, 16130: 64, 18178: 72}

#  addrsizes
addrsizes = {0: 1, 1: 1024, 2: 4096, 3: 8192}

#  physics units /usr/ads/codes/dimensions

unitLabel = { \
  0:None, 1:'kg', 2:'m', 3:'V', 4:'A', 5:'mV', 6:'eV', 7:'J', 8:'s', 9:'min', 10:'h', \
  11:'Celsius', 12:'pm', 13:'msec', 14:'1/V', 15:'K', 16:'degree', 17:'keV', 18:'cm', \
  19:'mm', 20:'micron', 21:'+-5V/12b', 22:'+-10V/12', 23:'counts', 24:'10e14/cc', \
  25:'Vs', 26:'A/(m*m)', 27:'T', 28:'W', 29:'C', 30:'m^2', 31:'m^3', 32:'kA', \
  33:'W/m^2', 34:'W/m^2/nm', 35:'1/m', 36:'1/m^2', 37:'1/m^3', 38:'10e19/m^', \
  39:'mbar', 40:'Pa', 41:'bar', 42:'kV', 43:'mA', 44:'+-5V/409', 45:'+-10V/40', \
  46:'Hz', 47:'+5V/4095', 48:'+10V/409', 49:'l/min', 50:'1/s', 51:'MN/m', 52:'MJ', \
  53:'ASCII', 54:'V/A', 55:'m^3/h', 56:'MW', 57:'mm^2/s', 58:'m^2/s', 59:'W/(mm*K)', \
  60:'1/mm', 61:'dB', 62:'1/J', 63:'MW/m^2', 64:'kW/m^2', 65:'kA/s', 66:'T/s', \
  67:'W/(m^2*s', 68:'W/m^3', 69:'cnts/s', 70:'m/s', 71:'rad/s', 72:'GHz', 73:'N/A', \
  74:'nm', 75:'+-5V/16b', 76:'+-10V/16', 77:'AU', 78:'kW', 79:'J/m^2', 80:'V/m', \
  81:'Ph/(qm*s', 82:'1/(m^2*s', 83:'kA^2*s', 84:'Nm', 85:'+5V/12bi', 86:'+10V/12b', \
  87:'+-5V/13b', 88:'+-10V/13', 89:'+5V/13bi', 90:'+10V/13b', 91:'+-5V/819', \
  92:'+-10V/81', 93:'+5V/8191', 94:'+10V/819', 95:'+-5V/14b', 96:'+-10V/14', \
  97:'+5V/14bi', 98:'+10V/14b', 99:'+-5V/163', 100:'+-10V/16', 101:'+5V/1638', \
  102:'+10V/163', 103:'+-5V/15b', 104:'+-10V/15', 105:'+5V/15bi', 106:'+10V/15b', \
  107:'+-5V/327', 108:'+-10V/32', 109:'+5V/3276', 110:'+10V/327', 111:'+5V/16bi', \
  112:'+10V/16b', 113:'+-5V/655', 114:'+-10V/65', 115:'+5V/6553', 116:'+10V/655', \
  117:'nanosec', 118:'amu', 119:'pct', 120:'MHz', 122:'+-30V/65535', 123:'N', \
  124:'kN', 125:'MN', 126:'us', 127:'+1.58V/16383', 128:'1/(m^3*s)', \
  129:'J/m^3', 130:'1/cm^3', 131:'Nm/m^3', 132:'Web', 133:'Web/rad', 134:'Tm' \
}
expLabel  = {0: 'ASD', 1: 'AUGD', 2: 'WSA', 3: 'PRIV', 4: 'WSX'}
diagLabel = {1: 'DataAcqu', 2: 'Eichung', 3: 'Control', 4: 'Autonom'}
shotLabel = {0: 'TestShot', 1: 'GaugeShot', 2: 'NormalShot', 3: 'SummaryFile', 4: 'AUGSFMON2', 5: 'CalibShot', 6: 'directAFS'}
calibLabel = {0: 'NoCalib', 1: 'LinCalib', 2: 'LookUpTab', 3: 'extCalib'}
tbaseLabel = {0: 'ADC_intern', 1: 'PPG_prog', 2: 'Datablock', 4: 'Chain', 5: 'Condensed'}

expType   = dict_inv(expLabel)
diagType  = dict_inv(diagLabel)
shotType  = dict_inv(shotLabel)
diagType  = dict_inv(diagLabel)
calibType = dict_inv(calibLabel)
tbaseType = dict_inv(tbaseLabel)
unitType  = dict_inv(unitLabel)


def typeMap(col_in, col_out, val_in):
    return dtf.loc[dtf[col_in] == val_in][col_out].values[0]


def SFOmap(col_in, col_out, val_in):
    return sfof.loc[sfof[col_in] == val_in][col_out].values[0]


olbl   = pd.Series(sfof.SFOtypeLabel.values, index=sfof.SFOtypeID   ).to_dict()
ostruc = pd.Series(sfof.SFOtypeStruc.values, index=sfof.SFOtypeLabel).to_dict()
oid    = pd.Series(sfof.SFOtypeID.values   , index=sfof.SFOtypeLabel).to_dict()
oattr  = pd.Series(sfof.SFOattrs.values    , index=sfof.SFOtypeLabel).to_dict()
oid['Parameter'] = -1


def typeLength(SFfmt):
    if SFfmt in fmt2len.keys(): # char variable
        type_len = fmt2len[SFfmt]
    else: # numerical variable
        struc = typeMap('SFfmt', 'struc', SFfmt)
        type_len = np.dtype(struc).itemsize
    return type_len


def arrayShape(sfo):

    SFOlbl = sfo.SFOtypeLabel

    if SFOlbl in ('SignalGroup', 'Signal'):
        shape_arr = np.array(sfo.index[::-1][:sfo.num_dims])
    elif SFOlbl == 'TimeBase':
        shape_arr = np.array([sfo.n_steps])
    elif SFOlbl == 'AreaBase':
        shape_arr = np.array([sfo.size_x + sfo.size_y + sfo.size_z, sfo.n_steps])
    else:
        return None

    return shape_arr


def objectLength(sfo):

    shape_arr = arrayShape(sfo)
    type_len  = typeLength(sfo.dataFormat)

    return np.prod(shape_arr) * type_len
