import logging
import os
import platform
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
import s3fs
import xarray as xr
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

from ddc_utility.__version__ import version
from ddc_utility.auth import OAuth2BearerHandler
from ddc_utility.constants import (DEFAULT_AOI_BUCKET, DEFAULT_DDC_BUCKET,
                                   DEFAULT_DDC_HOST)
from ddc_utility.cube import open_cube
from ddc_utility.data_collections import DataCollection, prepare_data_layers
from ddc_utility.errors import (BadRequest, DdcClientError, DdcException,
                                DdcRequestError, Forbidden, HTTPException,
                                NotFound, ServerError, TooManyRequests,
                                Unauthorized)
from ddc_utility.utils import Geometry, IrrigationSchedule, TimeRange

log = logging.getLogger(__name__)


def authorize_request(method):
    def wrapper(self, *args, **kwargs):
        now = round(time.time())
        if self.auth is None or (self.auth.expires_at - now < 60):
            token = self.fetch_token()
            self.auth = OAuth2BearerHandler(
                token.get('access_token'), token.get('expires_at'))

        return method(self, *args, **kwargs)
    return wrapper


def authorize_s3_access(method):
    def wrapper(self, *args, **kwargs):
        now = round(time.time())

        if self.aws_s3 is None or (self.aws_session_exp - now < 60):
            temp_cred = self.fetch_temporary_credentials()
            self.aws_s3 = s3fs.S3FileSystem(
                key=temp_cred["AccessKeyId"],
                secret=temp_cred["SecretKey"],
                token=temp_cred["SessionToken"])
            self.aws_session_exp = temp_cred["expires_at"]

        return method(self, *args, **kwargs)
    return wrapper


class BaseClient:

    def __init__(
            self,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            host: Optional[str] = None,
            wait_on_rate_limit: Optional[bool] = False) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host

        self.wait_on_rate_limit = wait_on_rate_limit

        self.session = requests.Session()
        self.user_agent = (
            f"Python/{platform.python_version()} "
            f"Requests/{requests.__version__} "
            f"ddc_cube/{version}"
        )

    def request(self, method: str, route: str, params: Optional[Dict] = None,
                json_data: Optional[Dict] = None, auth: requests.auth.AuthBase = None, content_type: Optional[str] = None, accept: Optional[str] = None):

        headers = {
            "User-Agent": self.user_agent,
            "client_id": self.client_id
        }
        if content_type is not None:
            headers["Content-Type"] = content_type
        if accept is not None:
            headers["Accept"] = accept

        url = self.host + route

        log.debug(
            f"\nMaking API request: {method} {url}\n"
            f"Parameters: {params}\n"
            f"Headers: {headers}\n"
            f"Body: {json_data}"
        )

        with self.session.request(
                method, url, params=params, json=json_data, headers=headers, auth=auth) as response:

            if isinstance(response.content, bytes):
                log.debug(
                    "\nReceived API response: "
                    f"{response.status_code} {response.reason}\n"
                    f"Headers: {response.headers}\n"
                    f"Content: 'bytes content'"
                )

            else:
                log.debug(
                    "\nReceived API response: "
                    f"{response.status_code} {response.reason}\n"
                    f"Headers: {response.headers}\n"
                    f"Content: {response.content}"
                )

            if response.status_code == 400:
                raise BadRequest(response)
            if response.status_code == 401:
                raise Unauthorized(response)
            if response.status_code == 403:
                raise Forbidden(response)
            if response.status_code == 404:
                raise NotFound(response)
            if response.status_code == 429:
                if self.wait_on_rate_limit:
                    reset_time = int(response.headers["x-rate-limit-reset"])
                    sleep_time = reset_time - int(time.time()) + 1
                    if sleep_time > 0:
                        log.warning(
                            "Rate limit exceeded. "
                            f"Sleeping for {sleep_time} seconds."
                        )
                        time.sleep(sleep_time)
                    return self.request(method, route, params, json_data, auth, content_type, accept)
                else:
                    raise TooManyRequests(response)
            if response.status_code >= 500:
                raise ServerError(response)
            if not 200 <= response.status_code < 300:
                raise HTTPException(response)

            return response

    def _make_request(self, method, route, params={},
                      json_data=None, auth=None, content_type=None, accept=None):

        response = self.request(method, route, params=params,
                                json_data=json_data, auth=auth, content_type=content_type, accept=accept)

        # if return_type is dict and accept == "application/json":
        return response.json()
        # else:
        #    return response


class DdcClient(BaseClient):
    """
    Represents a Danube Data Cube client.

    Args:
        client_id (str): Danube Data Cube client id.
        client_secret (str): Danube Data Cube client secret.
        host (Optional[str] ): Alternative Danube Data Cube host url.

    Examples:
        # Create a DDC Client object for interacting with the DDC service
        >>> client = DdcClient(<client_id>, <client_secret>)

        # List the user's AOIs
        >>> DDC.get_all_aoi()

    """

    def __init__(self,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 host: Optional[str] = None) -> None:

        client_id = client_id or os.environ.get('DDC_CLIENT_ID')
        client_secret = client_secret or os.environ.get('DDC_CLIENT_SECRET')
        host = host or DEFAULT_DDC_HOST

        if not client_id or not client_secret:
            raise DdcException(
                'Both "client_id" and "client_secret" must be provided. '
                'Consider setting environment variables '
                'DDC_CLIENT_ID and DDC_CLIENT_SECRET.'
            )

        self.auth = None
        self.aws_s3 = None
        self.aws_session_exp = 0
        super().__init__(client_id, client_secret, host, False)

    @authorize_request
    def get_all_aoi(self, with_geometry: bool = True, desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get user's all area of interests (AOI).

        Args:
            with_geometry (bool, optional): Whether to retrive geometry values.
                Defaults to True.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as list of dictionaries (2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing AOI information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting AOIs.
        """

        params = {'user_id': self.client_id,
                  'with_geometry': with_geometry}

        route = "/aoi_manager/get_aoi"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting all aoi with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def get_aoi_by_id(self, aoi_id: int, desired_type: int = 1) -> Union[pd.DataFrame, Dict]:
        """
        Get user's area of interests (AOI) by ID.

        Args:
            aoi_id (int): ID of the AOI.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, Dict]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a dictionary containing AOI information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting the AOI.
        """

        params = {'user_id': self.client_id,
                  'aoi_id': aoi_id}

        route = "/aoi_manager/get_aoi"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting all aoi with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def create_aoi(self,
                   name: str,
                   geometry: Union[Geometry, Polygon, MultiPolygon, str],
                   time_range: Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]],
                   data_layers: Union[List[DataCollection], List[Dict]] = None,
                   is_dynamic: bool = False,
                   desired_type: int = 1
                   ) -> Union[pd.DataFrame, Dict]:
        """
        Create an area of interests (AOI).

        Args:
            name (str): The name of the area of interest.
            geometry (Union[Geometry, Polygon, MultiPolygon, str]): The geometry of the area of interest.
                This can be provided as a `ddc_utility.Geometry` object, a `shapely.Polygon`, a `shapely.MultiPolygon`, or as a WKT or GeoJSON string.
            time_range (Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]]):
                The time range for which the area of interest is defined.
                This can be provided as a `ddc_utility.TimeRange` object, a tuple of two `pandas.Timestamp` objects,
                or a tuple of two strings representing dates.
            data_layers (Union[List[DataCollection], List[Dict]], optional): A list of dictionaries representing data layers to associate with the AOI.
                Each dictionary should contain information about a specific data layer.
                Example:
                    [
                        {'name': 'S2L2A', 'bands': ['B04', 'B08']},
                        {'name': 'Meteorology', 'bands': ['Temp Avg', 'Prec']}
                    ]
                If None, the AOI cube will be created with an empty polygon.
                Defaults to None.
            is_dynamic (bool, optional): Whether the AOI is dynamic (True) or static (False).
                Defaults to False.
            desired_type (int, optional): Whether to return the result as a `pandas.DataFrame` (1) or as a dictionary (2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, Dict]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a dictionary containing AOI information.

        Raises:
            DdcRequestError: If an error occurs during the process of creating the AOI.

        """
        if not isinstance(time_range, TimeRange):
            time_range = TimeRange(*time_range)
        time_range_str = time_range.to_string(only_date=True)

        if not isinstance(geometry, Geometry):
            geometry = Geometry(geometry)
        geometry_str = geometry.to_string()

        if data_layers is None:
            data_layers_lst = []
        else:
            layers = []
            for layer in data_layers:
                if not isinstance(layer, DataCollection):
                    layer = DataCollection(
                        name=layer['name'], bands=layer['bands'])
                layers.append(layer)
            data_layers_lst = prepare_data_layers(layers)

        json_data = {
            "user_id": self.client_id,
            "name": name,
            "geometry": geometry_str,
            "start_date": time_range_str[0],
            "end_date": time_range_str[1],
            "is_dynamic": is_dynamic,
            "data_layers": {"data_sources": data_layers_lst}
        }

        route = "/aoi_manager/create_aoi"
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self._make_request(
                "POST", route, json_data=json_data, auth=self.auth, content_type=content_type, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during creating aoi with body {json_data} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def get_crop_types(self, desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get available crop types.

        Args:
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing crop type information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting crop types.
        """

        params = {'user_id': self.client_id}

        route = "/crop/get_type"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting crop types with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def create_crop_type(self,
                         crop_type_name: str,
                         desired_type: int = 1
                         ) -> Union[pd.DataFrame, Dict]:
        """
        Create crop type.

        Args:
            crop_type_name (str): Name of the crop type.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, Dict]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a dictionary containing crop type information.

        Raises:
            DdcRequestError: If an error occurs during the process of creating the growing season.

        """

        json_data = {
            "user_id": self.client_id,
            "crop_type_name": crop_type_name
        }

        route = "/crop/create_type"
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self._make_request(
                "POST", route, json_data=json_data, auth=self.auth, content_type=content_type, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during creating crop type with body {json_data} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def get_crop_variety(self, crop_type_id: int, desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get available crop types.

        Args:
            crop_type_id (int): ID of crop type.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing crop variety information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting crop variety.
        """

        params = {'user_id': self.client_id,
                  'crop_type_id': crop_type_id}

        route = "/crop/get_variety"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting crop variety with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def create_crop_variety(self,
                            crop_type_id: id,
                            crop_variety_name: str,
                            desired_type: int = 1
                            ) -> Union[pd.DataFrame, Dict]:
        """
        Create crop variety.

        Args:
            crop_type_id (id): ID of crop type.
            crop_variety_name (str): Name of the crop variety.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, Dict]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a dictionary containing crop variety information.

        Raises:
            DdcRequestError: If an error occurs during the process of creating the crop variety.

        """

        json_data = {
            "user_id": self.client_id,
            "crop_type_id": crop_type_id,
            "crop_variety_name": crop_variety_name
        }

        route = "/crop/create_variety"
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self._make_request(
                "POST", route, json_data=json_data, auth=self.auth, content_type=content_type, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during creating crop variety with body {json_data} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def get_crop_models(self, crop_type_id: int, desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get available crop model list.

        Args:
            crop_type_id (int): ID of crop type.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing crop model information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting crop models.
        """

        params = {'user_id': self.client_id,
                  'crop_type_id': crop_type_id}

        route = "/crop/get_model"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting crop models with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def run_crop_model(self,
                       aoi_id: int,
                       time_range: Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]],
                       sowing_date: Union[pd.Timestamp, str],
                       irrigation: List[Union[IrrigationSchedule, Tuple[Union[pd.Timestamp, str], float]]],
                       init_water_content: float,
                       growing_season_id: int,
                       crop_model_name: str,
                       desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Run crop model.

        Args:
            aoi_id (int): ID of the AOI.
            time_range (Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]]): Time range for the simulation.
            sowing_date (Union[pd.Timestamp, str]): Sowing date for the simulation.
            irrigation (List[Union[IrrigationSchedule, Tuple[Union[pd.Timestamp, str], float]]]): Irrigation schedule for the simulation.
            init_water_content (float): Initial water content for the simulation.
            growing_season_id (int): ID of the growing season.
            crop_model_name (str): Name of the crop model.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing crop model information.

        Raises:
            DdcRequestError: If an error occurs during the process of running crop model.

        """

        if not isinstance(time_range, TimeRange):
            time_range = TimeRange(*time_range)
        time_range_str = time_range.to_string(only_date=True)

        if not isinstance(sowing_date, pd.Timestamp):
            sowing_date = pd.Timestamp(sowing_date)
        sowing_date_str = sowing_date.isoformat(sep='T').split('T')[0]

        irrigation_str = []
        for irr in irrigation:
            if not isinstance(irr, IrrigationSchedule):
                irr = IrrigationSchedule(*irr)
            irrigation_str.append(irr.to_string(only_date=True))

        params = {
            "user_id": self.client_id,
            "aoi_id": aoi_id,
            "start_date": time_range_str[0],
            "end_date": time_range_str[1],
            "sowing_date": sowing_date_str,
            "irrigation": irrigation_str,
            "init_water_content": init_water_content,
            "growing_season_id": growing_season_id,
            "crop_model_name": crop_model_name
        }

        route = "/crop_model/run"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during running crop modle with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def get_growing_season(self, aoi_id: int, desired_type: int = 1) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get growing seasons for AOI.

        Args:
            aoi_id (int): ID of the AOI.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, List[Dict]]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a list of dictionary containing growing season information.

        Raises:
            DdcRequestError: If an error occurs during the process of requesting growing seasons.
        """

        params = {'user_id': self.client_id,
                  'aoi_id': aoi_id}

        route = "/growing_season/get_season"
        accept = "application/json"

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during getting growing seasons with params {params} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_request
    def create_growing_season(self,
                              aoi_id: int,
                              time_range: Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]],
                              sowing_date: Union[pd.Timestamp, str],
                              crop_type_id: int,
                              crop_variety_id: int,
                              crop_model_id: int,
                              desired_type: int = 1
                              ) -> Union[pd.DataFrame, Dict]:
        """
        Create growing season for AOI.

        Args:
            aoi_id (int): ID of the AOI.
            time_range (Union[TimeRange, Tuple[pd.Timestamp, pd.Timestamp], Tuple[str, str]]):
                The time range for which the growing season is defined.
                This can be provided as a `ddc_utility.TimeRange` object, a tuple of two `pandas.Timestamp` objects,
                or a tuple of two strings representing dates.
            sowing_date (Union[pd.Timestamp, str]): The date when the crop is sown.
            crop_type_id (int): ID of crop type.
            crop_variety_id (int): ID of crop variety.
            crop_model_id (int): ID of crop model.
            desired_type (int, optional): Whether to return the result as pandas.DataFrame (1) or as a dictionary(2).
                Defaults to 1.

        Returns:
            Union[pd.DataFrame, Dict]: Depending on the `desired_type` parameter,
            this function returns either a pandas DataFrame or a dictionary containing growing season information.

        Raises:
            DdcRequestError: If an error occurs during the process of creating the growing season.

        """

        if not isinstance(time_range, TimeRange):
            time_range = TimeRange(*time_range)
        time_range_str = time_range.to_string(only_date=True)

        if not isinstance(sowing_date, pd.Timestamp):
            sowing_date = pd.Timestamp(sowing_date)
        sowing_date_str = sowing_date.isoformat(sep='T').split('T')[0]

        json_data = {
            "user_id": self.client_id,
            "aoi_id": aoi_id,
            "start_date": time_range_str[0],
            "end_date": time_range_str[1],
            "sowing_date": sowing_date_str,
            "crop_type_id": crop_type_id,
            "crop_variety_id": crop_variety_id,
            "crop_model_id": crop_model_id
        }

        route = "/growing_season/create_season"
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self._make_request(
                "POST", route, json_data=json_data, auth=self.auth, content_type=content_type, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during creating growing season with body {json_data} from {route}"
            ) from error

        return self._process_response(response, desired_type)

    @authorize_s3_access
    def open_aoi_cube(self, aoi_id: int, bucket_name: str = DEFAULT_AOI_BUCKET) -> xr.Dataset:
        """
        Open AOI cube as an xarray.Dataset.

        Args:
            aoi_id (int): ID of the AOI.
            bucket_name (str, optional): Name of the S3 bucket where the zarr cube is stored.
                Defaults to `DEFAULT_AOI_BUCKET`.

        Returns:
            xr.Dataset: AOI cube.

        Raises:
            DdcClientError: If user don't have access to the bucket.
            DdcRequestError: If an error occurs during opening the cube.

        """

        zarr_path = f"s3://{bucket_name}/{aoi_id}_{self.client_id}.zarr"

        try:
            cube = open_cube(zarr_path, self.aws_s3)
        except PermissionError as error:
            raise DdcClientError(
                "User don't have access for this operation") from error
        except FileNotFoundError as error:
            raise DdcRequestError(
                f"Invalid aoi_id - no such aoi cube under{zarr_path}") from error
        except Exception as error:
            raise DdcRequestError(
                f"Error during getting AOI cube from {zarr_path}"
            ) from error
        return cube

    def open_ddc_cube(self, dataset_name: str, bucket_name: str = DEFAULT_DDC_BUCKET) -> xr.Dataset:
        """
        Open DDC dataset as an xarray.Dataset.

        Args:
            dataset_name (str): Name of the DDC dataset.
            bucket_name (str, optional): Name of the S3 bucket where the zarr cube is stored.
                Defaults to `DEFAULT_AOI_BUCKET`.

        Returns:
            xr.Dataset: DDC cube.

        Raises:
            DdcClientError: If user don't have access to the bucket.
            DdcRequestError: If an error occurs during opening the cube.

        """
        dataset_name_to_zarr_path = {
            "meteorology": {"zarr_name": "met.zarr", "group": "meteorology"},
            "forecast": {"zarr_name": "met.zarr", "group": "forecast"},
            "nhrl": {"zarr_name": "nhrl.zarr", "group": "nhrl"},
            "ecosystem": {"zarr_name": "ecosystem.zarr", "group": "ecosystem"},
            "taki": {"zarr_name": "met.zarr", "group": "soil"},
        }

        zarr_path_info = dataset_name_to_zarr_path.get(dataset_name)
        if not zarr_path_info:
            raise ValueError(
                f"Invalid dataset_name: {dataset_name} - must be one of {list(dataset_name_to_zarr_path.keys())}")

        zarr_path = f"s3://{bucket_name}/{zarr_path_info['zarr_name']}"

        try:
            cube = open_cube(zarr_path=zarr_path,
                             s3=s3fs.S3FileSystem(anon=True),
                             group=zarr_path_info['group'])
        except PermissionError as error:
            raise DdcClientError(
                "User don't have access for this operation") from error
        except Exception as error:
            raise DdcRequestError(
                f"Error during getting DDC cube from {zarr_path}"
            ) from error
        return cube

    def _process_response(self, data: Any, desired_type: int = None):
        if desired_type == 1:
            if isinstance(data, list):
                return pd.DataFrame(data)
            if isinstance(data, dict):
                return pd.DataFrame([data])
            else:
                raise ValueError(
                    f"Can't post-process API response -- {type(data)} is invalid with desired_type of {desired_type}")
        else:
            return data

    def fetch_token(self) -> Dict:
        """Fetch token from a remote token endpoint."""

        route = "/get_token"
        accept = "application/json"
        content_type = "application/json"
        json_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        now = time.time()

        try:
            response = self._make_request(
                "POST", route, json_data=json_data, content_type=content_type, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during fetching token from {route}"
            ) from error

        if "Error" in response:
            raise DdcClientError(
                f"Error during fetching token for user: {response['Error']}")

        if response['token_type'].lower() != 'bearer':
            raise DdcRequestError(
                f"Expected token_type to equal 'bearer',but got {response['token_type']} instead")

        response['expires_at'] = now + int(response.pop('expires_in'))

        return response

    @authorize_request
    def fetch_temporary_credentials(self) -> Dict:
        """Fetch token from a remote token endpoint."""

        route = "/get_temp_cred"
        accept = "application/json"
        params = {'user_id': self.client_id}

        try:
            response = self._make_request(
                "GET", route, params=params, auth=self.auth, accept=accept)

        except HTTPException as error:
            raise DdcRequestError(
                f"Error during fetching temporary credential from {route}"
            ) from error

        response = response["Credentials"]

        response["expires_at"] = int(time.mktime(time.strptime(
            response.pop("Expiration"), "%Y-%m-%dT%H:%M:%SZ")))

        return response
