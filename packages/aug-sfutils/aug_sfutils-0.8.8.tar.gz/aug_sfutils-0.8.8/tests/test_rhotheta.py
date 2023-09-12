import aug_sfutils as sf
import numpy as np

time = 3.
eqm = sf.EQU(39649)

geq = sf.to_geqdsk(eqm, t_in=time)

# repeat here to have access to equ with correct cocos convention
eqm.to_coco(cocos_out=1)

eq = eqm
#eq = equ
jt = np.argmin(np.abs(eq.time - time))

t_int = [3.004, 6.7]
Rc, Zc = sf.cross_surf(eq, rho=1., r_in=1.65, z_in=0, theta_in=0, coord_in='rho_pol')
#Rt, Zt = sf.rhoTheta2rz(eq, rho=eq.pfl[jt, max(eq.lpfp)], theta_in=0, t_in=eq.time[jt], coord_in='Psi')
Rcs, Zcs = sf.cross_sep(eq, r_in=1.65, z_in=0, theta_in=0, t_in=t_int)

print(Rc)
#print(Rt)
print(Rcs)
