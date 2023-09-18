import warnings
import numpy as np
from exojax.spec.set_ditgrid import minmax_ditgrid_matrix
from exojax.spec.set_ditgrid import precompute_modit_ditgrid_matrix

def setdgm_exomol(mdb, fT, Parr, R, molmass, dit_grid_resolution, *kargs):
    """Easy Setting of DIT Grid Matrix (dgm) using Exomol.

    Args:
       mdb: mdb instance
       fT: function of temperature array
       Parr: pressure array
       R: spectral resolution
       molmass: molecular mass
       dit_grid_resolution: resolution of dgm
       *kargs: arguments for fT

    Returns:
       DIT Grid Matrix (dgm) of normalized gammaL

    Example:

       >>> fT = lambda T0,alpha: T0[:,None]*(Parr[None,:]/Pref)**alpha[:,None]
       >>> T0_test=np.array([1100.0,1500.0,1100.0,1500.0])
       >>> alpha_test=np.array([0.2,0.2,0.05,0.05])
       >>> dit_grid_resolution=0.2
       >>> dgm_ngammaL=setdgm_exomol(mdbCH4,fT,Parr,R,molmassCH4,dit_grid_resolution,T0_test,alpha_test)
    """
    set_dgm_minmax = []
    Tarr_list = fT(*kargs)
    for Tarr in Tarr_list:
        SijM, ngammaLM, nsigmaDl = exomol(mdb, Tarr, Parr, R, molmass)
        set_dgm_minmax.append(minmax_ditgrid_matrix(ngammaLM, dit_grid_resolution))
    dgm_ngammaL = precompute_ditgrid_matrix(set_dgm_minmax, dit_grid_resolution=dit_grid_resolution)
    return jnp.array(dgm_ngammaL)
