"""Package antmocdata.solution
Processing ANT-MOC solution data, including reaction rates and fluxes.
"""

from .rxvtk import load_vtk, normalize
from .rxh5 import convert_h5_to_vtk