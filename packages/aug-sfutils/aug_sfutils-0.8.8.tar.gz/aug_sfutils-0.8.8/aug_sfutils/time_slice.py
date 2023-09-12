import logging
import numpy as np
from scipy import interpolate
from aug_sfutils import time_no_elm

logger = logging.getLogger('trview.time_slice')
logger.setLevel(logging.INFO)


def map2tgrid_rho_err(raw_d, t_out, nshot=None, noELMs=False, dt_out=None):

# t_out is the output regular time grid

    t1 = raw_d['tgrid']
    nt_in, nx_in = raw_d['rhop'].shape
    nt_out = len(t_out)

    if nt_in == 1:
        x_out   = np.tile(raw_d['rhop'    ][0, :], nt_out).reshape((nt_out, nx_in)) 
        y_out   = np.tile(raw_d['data'    ][0, :], nt_out).reshape((nt_out, nx_in)) 
        err_out = np.tile(raw_d['data_err'][0, :], nt_out).reshape((nt_out, nx_in)) 
        return x_out, y_out, err_out

# Remove data close to ELMs

    if (nshot is not None) and noELMs:
        ind_elm = time_no_elm.time_no_elm(nshot, t1) # Time points too close to ELMs
        ind_ok = (~ind_elm)
    else:
        ind_ok = np.ones(nt_in, dtype=bool)

    t_in   = raw_d['tgrid'   ][ind_ok]
    x_in   = raw_d['rhop'    ][ind_ok, :]
    y_in   = raw_d['data'    ][ind_ok, :]
    err_in = raw_d['data_err'][ind_ok, :]

    dt_in = np.min(np.diff(t_in))

# Remove infinite/nan from measurement uncertainties

    ymax = np.nanmax(y_in)
    non_fin_y   = (~np.isfinite(y_in))
    non_fin_err = (~np.isfinite(err_in))
    y_in[non_fin_y] = 0
    y_in[non_fin_err] = 0
    err_in[non_fin_y] = np.nan #1e3*ymax
    err_in[non_fin_err] = np.nan #1e3*ymax

# git 23.04.21
    ind_zero = (y_in == 0)
    y_in[ind_zero] = np.nan 
    err_in[ind_zero] = np.nan

# In case of no valid points in time interval

    fx = interpolate.interp1d(t_in, x_in, axis=0)
    fy = interpolate.interp1d(t_in, y_in, axis=0)
    fe = interpolate.interp1d(t_in, err_in, axis=0)

# Create intermediate grid
    if dt_out is None:
        dt_out = t_out[-1] - t_out[-2]

    x_out   = np.zeros((nt_out, nx_in))
    y_out   = np.zeros((nt_out, nx_in))
    err_out = np.zeros((nt_out, nx_in))

    tbins = np.zeros(nt_out + 1)
    tbins[0] = t_out[0] - 0.5*dt_out
    tbins[1: -1] = 0.5*(t_out[1:] + t_out[:-1])
    tbins[-1] = t_out[-1] + 0.5*dt_out
    indbin = np.searchsorted(tbins, t_in, side='left')
    for jt in range(nt_out):
        (tind, ) = np.where(indbin == jt+1)
        if np.isnan(y_in[tind, :]).all():
            logger.debug(' All nan at t=%.3f', t_out[jt])
        if tind.any():
            x_out[jt]   = np.nanmean(x_in[tind, :], axis=0)
            y_out[jt]   = np.nanmean(y_in[tind, :], axis=0)
#            err_out[jt] = np.linalg.norm(err_in[tind, :], axis=0)/len(tind)
            err_out[jt] = np.nanmean(err_in[tind, :], axis=0)
        else:
            tloc = t_out[jt]
            if (tloc >= t_in[0]) and (tloc <= t_in[-1]): #interpolate internal points
                x_out  [jt] = fx(tloc)
                y_out  [jt] = fy(tloc)
                err_out[jt] = fe(tloc)
            else:
                if (tloc < t_in[0] - dt_in): # set to 0 beyond dt
                    x_out[jt] = x_in[0]
                    y_out[jt] = 0
                    err_out[jt] = 1e3*ymax
                elif tloc < t_in[0]:      # extrapolate within dt
                    tfac = (tloc - t_in[0])/(t_in[1] - t_in[0])
                    x_out[jt] = x_in[0] + tfac*(x_in[1] - x_in[0])
                    y_out[jt] = y_in[0] + tfac*(y_in[1] - y_in[0])
                    err_out[jt] = err_in[0]
                if (tloc > t_in[-1] + dt_in) :
                    x_out[jt] = x_in[-1]
                    y_out[jt] = 0
                    err_out[jt] = 1e3*ymax
                elif tloc > t_in[-1]:
                    tfac = (tloc - t_in[-1])/(t_in[-2] - t_in[-1])
                    x_out[jt] = x_in[-1] + tfac*(x_in[-2] - x_in[-1])
                    y_out[jt] = y_in[-1] + tfac*(y_in[-2] - y_in[-1])
                    err_out[jt] = err_in[-1]

    err_out[np.isnan(err_out)] = 1e3*ymax

    return x_out, y_out, err_out



def map2tgrid(t_out, t_in, sig_input, nshot=None, noELMs=False, dt_out=None, ind_elm=None, indbin=None):

# Remove data close to ELMs

    if ind_elm is None:
        if (nshot is not None) and noELMs:
            logger.info('Discard times close to ELMs')
            ind_elm = time_no_elm.time_no_elm(nshot, t_in) # Time points too close to ELMs
            logger.info('#ELM discarded: %d out of %d', np.sum(ind_elm), len(t_in))
        else:
            ind_elm = []

    dt_left  = t_in[ 1] - t_in[ 0]
    dt_right = t_in[-1] - t_in[-2]
    nt_out = len(t_out)

# Create intermediate grid
# Output grid must be regular!

    if indbin is None:
        if dt_out is None:
            dt_out = t_out[-1] - t_out[-2]
        tbins = np.zeros(nt_out + 1)
        tbins[ 0] = t_out[ 0] - 0.5*dt_out
        tbins[-1] = t_out[-1] + 0.5*dt_out
        tbins[1: -1] = 0.5*(t_out[1:] + t_out[:-1])
        indbin = np.searchsorted(tbins, t_in, side='left')

# Back-up for empty slices

    sig_in = sig_input.copy()
    fy = interpolate.interp1d(t_in, sig_in, axis=0)
    sig_in[ind_elm, ...] = np.nan

    if sig_in.ndim == 1:
        sig_out = np.zeros(nt_out)
    else:
        dims = np.append(nt_out, sig_in.shape[1:])
        sig_out = np.zeros(dims)

    for jt in range(nt_out):
        (tind,) = np.where(indbin == jt+1)
        if tind.any():
            sig_out[jt] = np.nanmean(sig_in[tind], axis=0)
        else:
            tloc = t_out[jt]
            if (tloc >= t_in[0]) and (tloc <= t_in[-1]): #interpolate internal points
                sig_out[jt] = fy(tloc)
            else:
                if (tloc < t_in[0] - dt_left): # set to 0 beyond dt
                    sig_out[jt] = 0
                elif tloc < t_in[0]:      # extrapolate within dt
                    tfac = (tloc - t_in[0])/(t_in[1] - t_in[0])
                    sig_out[jt] = sig_in[0] + tfac*(sig_in[1] - sig_in[0])
                if (tloc > t_in[-1] + dt_right) : # set to 0 beyond dt
                    sig_out[jt] = 0
                elif tloc > t_in[-1]:      # extrapolate within dt
                    tfac = (tloc - t_in[-1])/(t_in[-2] - t_in[-1])
                    sig_out[jt] = sig_in[-1] + tfac*(sig_in[-2] - sig_in[-1])

    return sig_out, ind_elm, indbin
