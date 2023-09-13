
from typing import Dict, List, Optional


class DanubeDataCubeMetadata:

    def __init__(self):
        self._metadata = _DDC_METADATA

    @property
    def dataset_names(self) -> List[str]:
        return [ds_id for ds_id in self._metadata['datasets']]

    def dataset(self, dataset_name: str) -> Optional[Dict]:
        dataset = dict(self._dataset_direct(dataset_name))
        dataset.pop('variables')
        return dataset if dataset is not None else None

    def dataset_vars(self, dataset_name: str, default=None) -> \
            Optional[Dict]:
        variables = self._dataset_vars_direct(dataset_name)
        return dict(variables) if variables else default

    def dataset_vars_names(self, dataset_name: str, default=None) -> \
            Optional[List[str]]:
        variables = self._dataset_vars_direct(dataset_name)
        return [var_name for var_name in variables] if variables else default

    def dataset_var(self, dataset_name: str, variable_name: str, default=None) \
            -> Optional[Dict]:
        var = self._dataset_var_direct(dataset_name, variable_name)
        return dict(var) if var else default

    def _dataset_direct(self, dataset_name: str) -> Optional[Dict]:
        return self._metadata['datasets'].get(dataset_name.upper())

    def _dataset_vars_direct(self, dataset_name: str) \
            -> Optional[Dict]:
        dataset = self._dataset_direct(dataset_name)
        return dataset.get('variables') if dataset else {}

    def _dataset_var_direct(self, dataset_name: str, variable_name: str) \
            -> Optional[Dict]:
        variables = self._dataset_vars_direct(dataset_name)
        return variables.get(variable_name) if variables else {}


_FORECAST_VAR_METADATA = {
    'temp_min': {
        'standard_name': 'min_air_temperature_2m',
        'long_name': 'Minimum temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'temp_max': {
        'standard_name': 'max_air_temperature_2m',
        'long_name': 'Maximum temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'temp_avg': {
        'standard_name': 'avg_air_temperature_2m',
        'long_name': 'Average temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'prec': {
        'standard_name': 'precipitation_mm',
        'long_name': 'Precipitation amount',
        'units': 'mm',
        'coverage_content_type': 'physical_measurement',
    },
    'et0': {
        'standard_name': 'evapotranspiration_mm',
        'long_name': 'Potential evapotranspiration',
        'units': 'mm',
        'coverage_content_type': 'physical_measurement',
    }
}


_MET_VAR_METADATA = {
    'temp_min': {
        'standard_name': 'min_air_temperature_2m',
        'long_name': 'Minimum temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'temp_max': {
        'standard_name': 'max_air_temperature_2m',
        'long_name': 'Maximum temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'temp_avg': {
        'standard_name': 'avg_air_temperature_2m',
        'long_name': 'Average temperature (2 m)',
        'units': '°C',
        'coverage_content_type': 'physical_measurement',
    },
    'prec': {
        'standard_name': 'precipitation_mm',
        'long_name': 'Precipitation amount',
        'units': 'mm',
        'coverage_content_type': 'physical_measurement',
    },
    'eto': {
        'standard_name': 'evapotranspiration_mm',
        'long_name': 'Potential evapotranspiration',
        'units': 'mm',
        'coverage_content_type': 'physical_measurement',
    }
}


_SOIL_VAR_METADATA = {
    'soil1': {
        'standard_name': '',
        'long_name': '',
        'units': "",
        'coverage_content_type': '',
    }
}


_NHRL_VAR_METADATA = {
    'nhrl': {
        'standard_name': 'landcover_categories',
        'long_name': 'Land cover and land use thematic map',
        'units': "thematic class/category",
        'coverage_content_type': 'thematic_classification',
        'flag_meanings': '["other_paved_or_non-paved_artificial_surfaces", "road_network", "railway_network", "bare_soil", "cereals", "row_crops", "alfalfa", "rapeseed", "grasslands", "orchards", "vineyards", "heterogeneous_vegetated_surfaces_in_built-up_environment", "shrubland", "broadleaved_trees", "coniferous_trees", "grasslands_with_shrubs", "heterogeneous_grassland_with_periodic_water_effect", "salt_steppes_and_meadows", "wetlands", "reeds", "water_surfaces", "single-floor_buildings", "high_buildings"]',
        'flag_values': '[12, 13, 14, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 36, 37, 41, 43, 51, 111, 112]',
        'flag_colors': '["#828282", "#4e4e4e", "#000000", "#e1e1e1", "#ffffbe", "#ffebaf", "#d3ffbe", "#aaff00", "#abcd66", "#b0643c", "#ffaa00", "#ffff00", "#448970", "#38a800", "#267300", "#f5f57a", "#cdf57a", "#67f070", "#73b2ff", "#d69dbc", "#0070ff", "#ff0000", "#a80000"]',
    }
}

_ECOSYSTEM_VAR_METADATA = {
    'ecosystem': {
        'standard_name': 'ecosystem_categories',
        'long_name': 'Ecosystem categories thematic map',
        'units': "thematic class/category",
        'coverage_content_type': 'thematic_classification',
        'flag_meanings': '["low_buildings", "high_buildings", "paved_roads", "dirt_roads", "railways", "other_paved_or_non-paved_artificial_areas", "green_urban_areas_with_trees", "green_urban_areas_without_trees", "arable_land", "vineyards", "fruit_and_berry_and_other_plantations", "energy_crops", "complex_cultivation_patterns_with_scattered_buildings", "complex_cultivation_patterns_without_buildings", "open_sand_steppes", "closed_sand_steppes", "salt_steppes_and_meadows_(grasslands_affected_by_salinisation_included)", "calcareous_open_rocky_grasslands", "siliceous_open_rocky_grasslands", "closed_grasslands_in_hills_and_mountains_or_on_cohesive_soil", "other_herbaceous_vegetation", "beech_forests", "sessile_oak-hornbeam_forests", "turkey_oak_forests", "downy_oak_forests", "scots_pine_stands_of_western_transdanubia", "deciduous_stands_of_western_transdanubia_mixed_with_scots_pine", "native_poplar_dominated_forests", "pioneer_forests_of_hilly_and_mountainous_regions", "pedunculate_oak-hornbeam_forests", "pedunculate_oak_forests_monospecific_or_mixed_with_ash", "forests_dominated_by_other_native_tree_species", "other_mixed_deciduous_forests", "riverine_willow-poplar_woodlands", "riverine_hardwood_forests", "pedunculate_oak_forests_monospecific_or_mixed_with_ash", "alder_forests", "pedunculate_oak-hornbeam_forests_(with_excess_water)", "willow_woods_outside_the_floodplain", "poplar_woods_outside_the_floodplain", "birch_woodland", "turkey_oak_forests_with_excess_water", "forests_dominated_by_other_native_tree_species_with_excess_water", "other_mixed_deciduous_forests_with_excess_water", "conifer-dominated_plantations", "black_locust-dominated_mixed_plantations", "plantations_dominated_by_non-native_poplar_and_willow_species", "plantations_of_other_non-native_tree_species", "clearcut", "forest_stand_under_regeneration", "other_ligneous_vegetation_woodlands", "tall-herb_vegetation_of_marshes_and_fens_standing_in_water", "fens_and_mesotrophic_wet_meadows_grasslands_with_periodic_water_effect", "swamp_woodlands", "water_bodies", "water_courses"]',
        'flag_values': '[1110, 1120, 1210, 1220, 1230, 1310, 1410, 1420, 2100, 2210, 2220, 2230, 2310, 2320, 3110, 3120, 3200, 3310, 3320, 3400, 3500, 4101, 4102, 4103, 4104, 4105, 4106, 4107, 4108, 4109, 4110, 4111, 4112, 4201, 4202, 4301, 4302, 4303, 4304, 4305, 4306, 4307, 4308, 4309, 4401, 4402, 4403, 4404, 4501, 4502, 4600, 5110, 5120, 5200, 6100, 6200]',
        'flag_colors': '["#FF0000", "#A80000", "#9C9C9C", "#CCCCCC", "#828282", "#FFBEBE", "#A8A800", "#D7D79E", "#FFEBBE", "#FFD37F", "#FFAA00", "#E69800", "#FFB582", "#FFFF73", "#D1FF73", "#D1FF73", "#CFBBA7", "#C8DC87", "#C8DC87", "#A1B36D", "#98E600", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#38A800", "#70A800", "#70A800", "#50B400", "#50B400", "#50B400", "#50B400", "#50B400", "#50B400", "#50B400", "#50B400", "#50B400", "#507300", "#507300", "#507300", "#507300", "#737300", "#737300", "#267300", "#BEE8FF", "#73DFFF", "#00C5FF", "#004DA8", "#002673"]',
    }
}


_DDC_METADATA = dict(
    datasets={
        'FORECAST': dict(
            title='OMSZ Meteorological Forecast',
            description='Interpolated grids of meteorological forecast.',
            variables=_FORECAST_VAR_METADATA
        ),
        'METEOROLOGY': dict(
            title='OMSZ Meteorological Measurements',
            description='Interpolated grids of meteorological measurements.',
            variables=_MET_VAR_METADATA
        ),
        'SOIL': dict(
            title='Soil data',
            description='',
            variables=_SOIL_VAR_METADATA
        ),
        'NHRL': dict(
            title='National High-Resolution Layer of Hungary (NHRL)',
            description='Derived from EO satellite imagery, GIS data and in-situ measurements. The data generation is based on Random Forest machine learning algorithm.',
            copyright='Lechner Nonprofit Ltd.',
            institution='Lechner Nonprofit Ltd., Directorate of Geospatial Services',
            licence='This work is licensed under a Creative Commons Attribution 4.0 International License (https://creativecommons.org/licenses/by/4.0/).',
            variables=_NHRL_VAR_METADATA,
        ),
        'ECOSYSTEM': dict(
            title='Ecosystem Map of Hungary',
            description='Derived from EO satellite imagery, GIS data and in-situ measurements. The data generation is based on Random Forest machine learning algorithm.',
            copyright='Hungarian Ministry of Agriculture',
            institution='Lechner Nonprofit Ltd., Directorate of Geospatial Services',
            licence='The downloaded databases are free to use as long as references to the source are provided. Citacion (obligatory) - The database/analysis has been created using the Ecosystem Map of Hungary (project KEHOP-430-VEKOP-15-2016-00001, Ministry of Agriculture, 2019) DOI - 10.34811/osz.alapterkep',
            variables=_ECOSYSTEM_VAR_METADATA,

        ),
    }
)
