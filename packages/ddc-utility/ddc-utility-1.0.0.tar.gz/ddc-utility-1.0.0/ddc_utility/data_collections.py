from pydantic import BaseModel, model_validator, field_validator, computed_field
from typing import Optional, List, Dict


DDC_DATASETS = {
    'HR_VPP_DAILY': {'title': 'Daily Vegetation Phenology and Productivity', 'bands': ['LAI', 'NDVI', 'FAPAR', 'QFLAG2', 'PPI']},
    'HR_VPP_ST': {'title': '10-daily Seasonal Trajectories', 'bands': ['PPI', 'QFLAG']},
    'S2L2A': {'title': 'Sentinel-2', 'bands': ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12', 'CLD']},
    'S1GRD': {'title': 'Sentinel-1 GRD', 'bands': ['VV', 'VH', 'localIncidenceAngle', 'scatteringArea', 'shadowMask']},
    'Meteorology': {'title': 'Meteorology', 'bands': ['ET0', 'Temp Avg', 'Temp Min', 'Temp Max', 'Prec']},
    'Soil': {'title': 'Soil', 'bands': ['hyd_cur_K0', 'hyd_cur_L', 'hyd_cur_alp', 'hyd_cur_m', 'hyd_cur_n', 'hyd_cur_thr', 'hyd_cur_ths', 'hydcon', 'moi_cur_alp', 'moi_cur_m', 'moi_cur_n', 'moi_cur_thr', 'moi_cur_ths', 'watcap', 'watcnt', 'watwil']},
    'Nhrl': {'title': 'Nhrl', 'bands': ['nhrl']},
    'Ecosystem': {'title': 'Ecosystem', 'bands': ['ecosystem']},
    'S2L2A_PC': {'title': 'Sentinel-2 PC', 'bands': ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12']}
}


class DataCollection(BaseModel):

    # title: str
    name: str
    bands: Optional[List[str]]

    @field_validator('name')
    @classmethod
    def check_name(cls, val):
        if val not in DDC_DATASETS:
            raise ValueError(
                f'Invalid dataset name, name must be in {list(DDC_DATASETS)}')
        return val

    @model_validator(mode="after")
    def check_bands(self):
        orig_bands = DDC_DATASETS[self.name]["bands"]
        new_bands = []

        for band in self.bands:
            if band in orig_bands:
                new_bands.append(band)
        self.bands = new_bands
        return self

    @computed_field
    @property
    def title(self) -> str:
        return DDC_DATASETS[self.name]["title"]


def prepare_data_layers(data_layers: List[DataCollection]) -> List[Dict]:

    layers = []
    available_datasets = list(DDC_DATASETS)

    for collection in data_layers:
        layers.append(collection.model_dump())
        available_datasets.remove(collection.name)

    for rest in available_datasets:
        layers.append(DataCollection(name=rest, bands=[]).model_dump())

    return layers
