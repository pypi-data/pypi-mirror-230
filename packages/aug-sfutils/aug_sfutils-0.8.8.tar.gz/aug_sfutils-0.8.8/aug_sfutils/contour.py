import numpy as np
from aug_sfutils import SFREAD, str_byt

Rlim_xml = np.array([ \
    0.2887, 1.1357, 1.1383, 1.1408, 1.1431, 1.1450, 1.2466, 1.2500, 1.2588, 1.2664, \
    1.2729, 1.2783, 1.2854, 1.2878, 1.2872, 1.2829, 1.2360, 1.2340, 1.2437, 1.2440, \
    1.2440, 1.2799, 1.2799, 1.2804, 1.3225, 1.3256, 1.4590, 1.4629, 1.5541, 1.5553, \
    1.5553, 1.5675, 1.5793, 1.5794, 1.6140, 1.6352, 1.6361, 1.6431, 1.6581, 1.6737, \
    1.7021, 1.7075, 1.7155, 1.7274, 1.7389, 1.7521, 1.9944], dtype=np.float32)

Zlim_xml = np.array([ \
    -1.1698, -0.6580, -0.6579, -0.6585, -0.6597, -0.6615, -0.8198, -0.8273, -0.8422, -0.8575, \
    -0.8733, -0.8895, -0.9229, -0.9569, -0.9740, -0.9871, -1.1234, -1.1280, -1.1418, -1.1424, \
    -1.1431, -1.1230, -1.1000, -1.0981, -1.0635, -1.0624, -1.0624, -1.0642, -1.1732, -1.1764, \
    -1.1840, -1.2090, -1.2090, -1.2077, -1.0784, -0.9993, -0.9970, -0.9720, -0.9368, -0.9093, \
    -0.8633, -0.8569, -0.8499, -0.8432, -0.8397, -0.8264, -0.5502], dtype=np.float32)


Rlim_aug = Rlim_xml
Zlim_aug = Zlim_xml
ds_vert = np.hypot(Rlim_aug[1:] - Rlim_aug[:-1], Zlim_aug[1:] - Zlim_aug[:-1])
s_vert = np.append(0, np.cumsum(ds_vert)) - 1.


def getgc2(nshot=30136):
    """
    Returns first wall contours for plotting and plasma-facing part
    """
    ygc_sf = [1996, 8646, 8650, 9401, 11300, 11301, 11320, 12751, 13231, 14051, 14601, 16310, 16315, 18204, 19551, 21485, 25891, 30136]
    ygc_sf = np.array(ygc_sf)
    nshot = np.max(ygc_sf[ygc_sf <= nshot])
    ygc = SFREAD(nshot, 'YGC')
    if ygc is not None:
        rrgc     = ygc.getobject('RrGC'  , cal=False)
        zzgc     = ygc.getobject('zzGC'  , cal=False)
        inxbeg   = ygc.getobject('inxbeg', cal=False)
        inxlen   = ygc.getobject('inxlen', cal=False)
        inxlps   = ygc.getobject('inxlps', cal=False)
        flag_use = ygc.getobject('ixplin', cal=False)
        gcnames  = ygc.getobject('chGCnm', cal=False)

    comp_d = {}
    pfc_d  = {}

    if gcnames is None:
        for jcom, leng in enumerate(inxlen):
            comp_d[jcom] = type('', (), {})() # empty object
            pfc_d [jcom] = type('', (), {})() # empty object
            jleft   = inxbeg[jcom] - 1
            jright  = jleft + leng
            jright2 = jleft + inxlps[jcom]
            comp_d[jcom].r = rrgc[jleft: jright]
            comp_d[jcom].z = zzgc[jleft: jright]
            pfc_d[jcom].r = rrgc[jleft: jright2]
            pfc_d[jcom].z = zzgc[jleft: jright2]
    else:
        for jcom, lbl in enumerate(gcnames):
            lbl = str_byt.to_str(lbl)
            jleft   = inxbeg[jcom] - 1
            jright  = jleft + inxlen[jcom]
            jright2 = jleft + inxlps[jcom]
            if flag_use[jcom] > 0:
#            if True:
#                print(lbl, inxlen[jcom], inxlps[jcom], flag_use[jcom])
    
                comp_d[lbl] = type('', (), {})()
                pfc_d [lbl] = type('', (), {})()
                comp_d[lbl].r = rrgc[jleft: jright]
                comp_d[lbl].z = zzgc[jleft: jright]
                pfc_d[lbl].r = rrgc[jleft: jright2]
                pfc_d[lbl].z = zzgc[jleft: jright2]

    return comp_d, pfc_d


def getgc(nshot=30136):
    """
    Returns first wall contours for plotting
    """
    comp_d, _ = getgc2(nshot=nshot)
    return comp_d


def rz2s(R_in, Z_in):

    R1 = Rlim_aug[ :-1]
    R2 = Rlim_aug[1:  ]
    Z1 = Zlim_aug[ :-1]
    Z2 = Zlim_aug[1:  ]
    R21 = R2 - R1
    Z21 = Z2 - Z1
    edge_len = np.hypot(R21, Z21)

    Rin = np.atleast_1d(R_in)
    Zin = np.atleast_1d(Z_in)
    sout = np.zeros_like(Rin)

    for jr, Rloc in enumerate(Rin):
        Zloc = Zin[jr]
        E1 = np.hypot(R1 - Rloc, Z1 - Zloc)
        E2 = np.hypot(R2 - Rloc, Z2 - Zloc)

# Find distance from the input Point to each polygon's edge
# https://stackoverflow.com/questions/39840030/distance-between-point-and-a-line-from-two-points
        distance = np.abs(R21*(Z1 - Zloc) - (R1 - Rloc)*(Z2 - Zloc)) / edge_len
        (indE1, ) = np.where(E1 > edge_len)
        distance[indE1] = E2[indE1]
        (indE2, ) = np.where(E2 > edge_len)
        distance[indE2] = E1[indE2]

# Find j of the closest edge
        jvert = np.argmin(distance)
# https://stackoverflow.com/questions/28931007/how-to-find-the-closest-point-on-a-line-segment-to-an-arbitrary-point
        x1 = R1[jvert]
        x2 = R2[jvert]
        y1 = Z1[jvert]
        dx = R21[jvert]
        dy = Z21[jvert]
        d2 = dx**2 + dy**2
        nx = ((Rloc - x1)*dx + (Zloc - y1)*dy) / d2
        Rclose = dx*nx + x1
        Zclose = dy*nx + y1

        sout[jr] = s_vert[jvert] + np.hypot(Rclose - R1[jvert], Zclose - Z1[jvert])

    return np.squeeze(sout)


def s2rz(s_in):

    s_in = np.atleast_1d(s_in)
    Rout = np.zeros_like(s_in)
    Zout = np.zeros_like(s_in)

# s_vert is monotonic -> ind has only one element (or zero, if s is too high)
    for js, slen in enumerate(s_in):
        s1 = s_vert[1:  ] - slen
        s2 = s_vert[ :-1] - slen
        (ind, ) = np.where(s1*s2 <= 0)
        if len(ind) > 0:
            jvert = ind[0]
        else:
            jvert = len(s1) - 1
# Interpolate R, z
        ds_ratio = (slen - s_vert[jvert])/ds_vert[jvert]
        Rout[js] = Rlim_aug[jvert] + ds_ratio*(Rlim_aug[jvert+1] - Rlim_aug[jvert])
        Zout[js] = Zlim_aug[jvert] + ds_ratio*(Zlim_aug[jvert+1] - Zlim_aug[jvert])

    return np.squeeze(Rout), np.squeeze(Zout)
