import xarray as xr
import numpy as np

import os



fn = 'GSWP3.BC.Tair.3hrMap.2013.nc'
ds = xr.open_dataset(fn) 

# print(ds)

data = ds["Tair"]

print(data[0])