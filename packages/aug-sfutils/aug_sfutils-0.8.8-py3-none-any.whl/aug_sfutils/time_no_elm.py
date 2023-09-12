import logging
import numpy as np
from aug_sfutils import SFREAD 

logger = logging.getLogger('trview.time_no_elm')


def time_no_elm(nshot, t_in, dt=[0.001, 0.005]):

    tloc = t_in
    ldel = np.zeros(len(t_in), dtype=bool)

    elm = SFREAD(nshot, 'ELM')
    if elm.status:
        t_elms = elm.getobject('tELM')
        if t_elms is None:
            logger.error('No time frames discarded close to ELMs')
            return ldel
#elm synchronized equlibrium - it will not use timepoits during the elms, CLISTE is not working well
        if np.max(t_elms > 0):
            told = -np.infty
            for it, t in enumerate(tloc):
                if any(t_elms<t):
                    last = np.argmax(t_elms[t_elms<t])
                    last_elm = t_elms[last]
                    if last < len(t_elms)-1:
                        next_elm = t_elms[last+1]
# Remove points up to 5ms after an ELM crash or 1 ms before
                        if t <= last_elm + dt[1] or t >= next_elm - dt[0] :
                            ldel[it] = True
                    else:
                        if t <= last_elm + dt[1]:
                            ldel[it] = True
                told = tloc[it-1]
        else:
            logger.error('No ELM correction')
    else:
        logger.error('No ELM correction')

    return ldel
