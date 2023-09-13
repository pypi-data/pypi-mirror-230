# DDC Utility

This is the Danube Data Cube Utility library, for retrieving data from the Danube Data Cube portal.

### Installation

```bash
pip install ddc-utility
```

### Usage

Users must have a valid DDC registration.

### Example
```
$ python

# Importing packages
>>> from ddc_utility.ddc import DanubeDataCube
>>> from ddc_utility.config import DdcCubeConfig, CustomCubeConfig
>>> from ddc_utility.cube import open_cube

# Setting DDC credentials
>>> os.environ['DDC_CLIENT_ID'] = ""
>>> os.environ['DDC_CLIENT_SECRET'] = ""

# Initialize DDC object 
>>> DDC = DanubeDataCube()

# Retrieve meteorological data from DDC
>>> cube_config = DdcCubeConfig(dataset_name='METEOROLOGY', variable_names=['prec', 'temp_min', 'temp_max'], danube_data_cube=DDC)
>>> cube = open_cube(cube_config)

# Retrieve custom cube based on users's AOI
>>> cube_config2 = CustomCubeConfig(dataset_name='<my_aoi_1.zarr>', variable_names=['NDVI', 'temp_avg', 'B04', 'B08'], danube_data_cube=DDC)
>>> cube2 = open_cube(cube_config2)

```
