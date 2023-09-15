import xarray as xr
import numpy as np

# TODO: check if I can change "coreframe" string to whatever user uses when "import coreframe as ___"
@xr.register_dataarray_accessor("coreframe")
class CoreFrameAccessor:
    # the reason we use data accessor, is because advanced xarray users might want to keep the xarray and 
    # access coreframe meethods through accessor

    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def to_dataarray(self):
        return self._obj

    def apply_by_time(self, itert, fun, from_CoreFrame = False, *args, **kwargs):
        def preprocess_itert(itert):
            """
            Adjust the frequency string to ensure bins are anchored to the start.
            """
            # If the frequency string already ends with an "S", return as is
            if itert.endswith('S'):
                return itert

            # Frequencies that are anchored to the start by default
            start_anchored = ['T', 'min', 'H', 'D', 'B']

            # Check if the frequency string matches any of the start-anchored frequencies
            if any(itert.endswith(anchor) for anchor in start_anchored):
                return itert
            
            # For all other frequencies, append an "S" to anchor to the start
            return itert + "S"

        def wrapper(x):
            return fun(x, *args, **kwargs)

        res = self._obj.resample(time = preprocess_itert(itert)).apply(wrapper)
        if from_CoreFrame:
            return CoreFrame(xarray=res)
        else:
            return res

    def apply_by_time_window(self, window, fun, from_CoreFrame = False, *args, **kwargs):
        """
        Applies a function in a rolling window fashion along the "time" axis.
        
        Parameters:
        - window (int): Size of the moving window. This is the number of observations used for calculating the statistic.
        - fun (function): The function to apply to each window. It should take a DataArray as its first argument and return a DataArray.
        - min_periods (int, optional): Minimum number of observations in window required to have a value (otherwise result is NA). Default is None.
        
        Returns:
        - xarray.DataArray: Result after applying the function.
        """
        
        res = self._obj.rolling(time=window, ).construct('window_dim').reduce(fun, *args, axis = -1, **kwargs)

        if from_CoreFrame:
            return CoreFrame(xarray=res)
        else:
            return res


    def apply_by_area(self, patch_size, fun, from_CoreFrame = False, *args, **kwargs):
        data_array = self._obj

        # Get the input array's shape
        input_shape = data_array.shape

        if len(input_shape) < 3:
            raise ValueError("The provided DataArray must have at least 3 dimensions.")
        
        if input_shape[1] % patch_size != 0 or input_shape[2] % patch_size != 0:
            raise ValueError("Shape of the DataArray has to be a multiple of patch_size.")
        
        # Reshape the DataArray to create non-overlapping patches
        reshaped_data = data_array.values.reshape(input_shape[0], input_shape[1] // patch_size, patch_size, input_shape[2] // patch_size, patch_size, *input_shape[3:])
        
        # Compute the function over the patch dimensions and reshape back to the reduced size
        patches_data = fun(reshaped_data, axis=(2, 4), *args, **kwargs).reshape(input_shape[0], input_shape[1] // patch_size, input_shape[2] // patch_size, *input_shape[3:])
        
        # Adjusting coordinates to match the new shape
        new_coords = {
            "time": data_array.coords["time"].values,
            "lat": data_array.coords["lat"].values[::patch_size] + patch_size // 2,
            "lon": data_array.coords["lon"].values[::patch_size] + patch_size // 2,
        }

        for coord in data_array.coords:
            if coord not in ["time", "lat", "lon"]:
                new_coords[coord] = data_array.coords[coord]
        
        # Convert patches data back to DataArray with adjusted coordinates
        res = xr.DataArray(patches_data, coords=new_coords, dims=data_array.dims)
        
        # Assuming attributes are to be preserved from the original DataArray
        res.attrs = data_array.attrs

        if from_CoreFrame:
            return CoreFrame(xarray=res)
        else:
            return res


# Wrapper class to simplify method calls, pass other methods and attributes to xarray, and handle operations
class CoreFrame:
    def __init__(self, data=None, coords=None, dims=None, xarray=None):
        if xarray is None:
            self._xarray_data = xr.DataArray(data, coords=coords, dims=dims)
        else:
            self._xarray_data = xarray

    def __getattr__(self, attr):
        return getattr(self._xarray_data, attr)
    
    def __repr__(self):
        return f"<CoreFrame wrapping {repr(self._xarray_data)}>"

    def __str__(self):
        return f"<CoreFrame wrapping {repr(self._xarray_data)}>"


    def to_xarray(self):
        return self._xarray_data

    def apply_by_time(self, itert, fun, *args, **kwargs):
        return self._xarray_data.coreframe.apply_by_time(itert, fun, from_CoreFrame=True, *args, **kwargs)
    
    def apply_by_time_window(self, itert, fun, *args, **kwargs):
        return self._xarray_data.coreframe.apply_by_time_window(itert, fun, from_CoreFrame=True, *args, **kwargs)

    def  apply_by_area(self, patch_size, fun, *args, **kwargs):
        return  self._xarray_data.coreframe.apply_by_area(patch_size, fun, from_CoreFrame=True, *args, **kwargs)