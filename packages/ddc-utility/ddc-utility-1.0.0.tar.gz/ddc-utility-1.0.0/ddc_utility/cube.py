
import xarray as xr
import s3fs


def open_cube(zarr_path: str, s3: s3fs.S3FileSystem, group: str = None):

    store = s3fs.S3Map(root=zarr_path, s3=s3, check=False)

    return xr.open_zarr(store, group)
