import xarray as xr

def open_dataset(path, mode="single", **kwargs):
    """
    Opens a dataset using xarray.
    
    Parameters:
    - path (str): The path to the file or files. For multi-file datasets, use a wildcard (e.g., 'folder/*.nc').
    - mode (str): Either 'single' for single files or 'multi' for multi-file datasets.
    - kwargs: Additional keyword arguments to pass to the xarray open functions.
    
    Returns:
    - xarray.Dataset: The opened dataset.
    """
    if mode == "single":
        return xr.open_dataset(path, **kwargs)
    elif mode == "multi":
        return xr.open_mfdataset(path, **kwargs)
    else:
        raise ValueError("Invalid mode. Choose either 'single' or 'multi'.")
