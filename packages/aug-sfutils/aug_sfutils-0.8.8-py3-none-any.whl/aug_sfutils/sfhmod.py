import logging
from aug_sfutils import sfmap
from aug_sfutils.shotfile import SHOTFILE as SF

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
logger = logging.getLogger('sfhmod')
logger.addHandler(hnd)
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)


class SFHMOD:


    def __init__(self, fin=None):

        self.sffull = SF(fin)


    def modtime(self, name, nt):
        '''Changes the size of the time dimension of a TB, AB, Sig or SigGroup (if related to a TB)'''

        sfo = self.sffull[name]
        SFOlbl = sfo.SFOtypeLabel
        if SFOlbl not in sfmap.DataObjects:
            logger.error('modtim accepts only TB, AB, Sig, SigName')
        elif SFOlbl in ('TimeBase', 'AreaBase'):
            sfo.n_steps = nt
        elif SFOlbl == 'Signal':
            sfo.index[-1] = nt
        elif SFOlbl == 'SignalGroup':
            tdim = None
            for robj in sfo.relobjects:
                if robj.SFOtypeLabel == 'TimeBase':
                    tdim = jrel
                    break
            if tdim is not None:
                sfo.index[3-tdim] = nt


    def modtimeall(self, tbase, nt):
        '''Changes the size of the time dimension of input TB plus all AB, Sig or SigGroup related to it'''

        sfo = self.sffull[tbase]
        if sfo.SFOtypeLabel not in ('TimeBase', 'Signal'):
            logger.error('modtimall needs a TB or SIG name')
            return

        self.modtime(tbase, nt)

        for sfo in self.sffull.SFobjects:
            for rel in sfo.relations:
                if rel == tbase:
                    self.modtime(sfo.objectName, nt)


    def modindex(self, sgr, index):
        '''Changes the dims of a SigGroup'''

        index = list(index)
        sfo = self.sffull[sgr]
        if sfo.SFOtypeLabel != 'SignalGroup':
            logger.error('modindex needs a SigGroup')
            return
        while len(index) < 4:
            index.append(1)
        sfo.index = index[::-1]


    def modareasize(self, abase, size_x=None, size_y=None, size_z=None):
        '''Changes the sizes of an AreaBase'''

        sfobj = self.sffull[abase]
        if sfo.SFOtypeLabel != 'AreaBase':
            logger.error('modareasize needs an AreaBase')
            return

        if size_x is not None:
            sfo.size_x = size_x
        if size_y is not None:
            sfo.size_y = size_y
        if size_z is not None:
            sfo.size_z = size_z


    def modareaall(self, abase, nx):
        '''Changes size_x of a space-1D AreaBase and the spatial dim of all related SigGroups'''
 
        sfo = self.sffull[abase]
        if sfo.SFOtypeLabel != 'AreaBase':
            logger.error('modareaall needs an AreaBase')
            return
        if sfo.size_y > 0:
            logger.error('modareaall works only with space-1d AreaBases')
            return

        sfo.size_x = nx

        for sfo in self.sffull.SFobjects:
            if sfo.SFOtypeLabel == 'SignalGroup':
                adim = None
                for jrel, rel in enumerate(sfo.relations):
                    if rel == abase:
                        adim = jrel
                        break
                if adim is not None:
                    sfo.index[3-adim] = nx


    def modpar(self, pset, pnam, data):
        '''Modify data content (and length) of parameter pnaf of ParSet pset'''

        par = self.sffull[pset].data[pnam]
        par.n_items = len(data)
        par[:par.n_items] = data[:]


    def write(self, fout='mytest.fsh'):

        sfh = SF(fout, sffull=self.sffull)
        sfh.dumpShotfile()


if __name__ == '__main__':

    fsfh = 'RAB00000.sfh'
    sfh = SFHMOD(fin=fsfh)
    sfh.modtimeall('time', 12)
    print('')
    sfh.modareaall('rho_in', 21)
    print('')
    sfh.write(fout='myrab.sfh')

    fsfh = 'TST00000.sfh'
    sfh = SFHMOD(fin=fsfh)    
    sfh.modpar('NBIpar', 'rtcena', [0.,1.,2.,3.] )
    print('')
    sfh.write(fout='mytra.sfh')
