
from typing import Optional, Union

import numpy as np
import pandas as pd
import shapely
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


class Bbox:
    """"Class for bounding box represented by four number.

    Args:
        minx (Union[str, int, float]): Minimum coordinate in x direction.
        miny (Union[str, int, float]): Minimum coordinate in y direction.
        maxx (Union[str, int, float]): Maximum coordinate in x direction.
        maxy (Union[str, int, float]): Maximum coordinate in y direction.
        precision (int): presion applied at rounding.
    """

    def __init__(self,
                 minx: Union[str, int, float],
                 miny: Union[str, int, float],
                 maxx: Union[str, int, float],
                 maxy: Union[str, int, float],
                 precision: Optional[int] = None):

        box = [minx, miny, maxx, maxy]
        if any([isinstance(v, str) for v in box]):
            box = list(map(float, box))

        if precision:
            box[0] = np.round(box[0], precision)
            box[1] = np.round(box[1], precision)
            box[2] = np.round(box[2], precision)
            box[3] = np.round(box[3], precision)

        self._minx = box[0]
        self._miny = box[1]
        self._maxx = box[2]
        self._maxy = box[3]
        self._precision = precision

    def __dict__(self):
        return {'minx': self.minx,
                'miny': self.miny,
                'maxx': self.maxx,
                'maxy': self.maxy}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):

        if len(v) == 4:
            precision = None
        elif len(v) == 5:
            precision = v[-1]
        else:
            raise ValueError(
                f'Invalid number of parameters of {len(v)} - bbox object '
                'must consist of four coordinate numbers and optionally '
                'a precision number.')

        try:
            minx, miny, maxx, maxy = tuple(map(float, (v[0], v[1],
                                                       v[2], v[3])))
            if not precision:
                base_prec = sorted(
                    map(str, (minx, miny, maxx, maxy)), key=len)[-1]
                precision = len(base_prec.split('.')[1])
            else:
                precision = int(precision)
        except (TypeError, ValueError) as error:
            raise ValueError(
                'Invalid input parameters - coordinates and precision '
                'must be convertable to numbers.') from error

        if minx > maxx:
            raise ValueError('minx must be smaller or equal to maxx')

        if miny > maxy:
            raise ValueError('miny must be smaller or equal to maxy')

        minx, miny, maxx, maxy = tuple(
            map(np.round, (minx, miny, maxx, maxy), [precision]*4))

        return cls(minx, miny, maxx, maxy, precision)

    @property
    def bbox(self):
        """Return the bounding box as a tuple."""
        return (self._minx, self._miny, self._maxx, self._maxy)

    @property
    def minx(self):
        """Return minimum value in x direction."""
        return self._minx

    @minx.setter
    def minx(self, value):
        """Set minimum value in x direction."""
        if self._precision:
            self._minx = np.round(float(value), self._precision)
        else:
            self._minx = float(value)

    @property
    def miny(self):
        """Return minimum value in y direction."""
        return self._miny

    @miny.setter
    def miny(self, value):
        """Set minimum value in y direction."""
        if self._precision:
            self._miny = np.round(float(value), self._precision)
        else:
            self._miny = float(value)

    @property
    def maxx(self):
        """Return maximum value in x direction."""
        return self._maxx

    @maxx.setter
    def maxx(self, value):
        """Set maximum value in x direction."""
        if self._precision:
            self._maxx = np.round(float(value), self._precision)
        else:
            self._maxx = float(value)

    @property
    def maxy(self):
        """Return maximum value in y direction."""
        return self._maxy

    @maxy.setter
    def maxy(self, value):
        """Set maximum value in y direction."""
        if self._precision:
            self._maxy = np.round(float(value), self._precision)
        else:
            self._maxy = float(value)


class TimeRange:
    """"Class for time range represented by two dates.

    Args:
        start_time (Union[str, pd.Timestamp]): Start date.
        end_time (Union[str, pd.Timestamp]): End date.
    """

    def __init__(self,
                 start_time: Union[str, pd.Timestamp],
                 end_time: Union[str, pd.Timestamp]):

        start_time = self.convert_time(start_time)
        end_time = self.convert_time(end_time)

        if start_time > end_time:
            raise ValueError("start_time must be smaller or equal to end_time")

        self._start_time = start_time
        self._end_time = end_time

    def __repr__(self):
        obj_name = f'<ddc_utility.{type(self).__name__}>'
        rep = f"{obj_name}\nstart_time: {self.start_time}\nend_time: {self.end_time}\n"
        return rep

    @property
    def time_range(self):
        """Return time range."""
        return [self._start_time, self._end_time]

    @property
    def start_time(self):
        """Return start time."""
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        """Set start time."""
        start_time = self.convert_time(value)
        if start_time <= self._end_time:
            self._start_time = start_time
        else:
            raise ValueError('start_time must be smaller or '
                             'equal to end_time')

    @property
    def end_time(self):
        """Return end time."""
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        """Set start time."""
        end_time = self.convert_time(value)
        if end_time >= self._start_time:
            self._end_time = end_time
        else:
            raise ValueError('end_time must be greater or '
                             'equal to start_time')

    def to_string(self, only_date=True):
        """Return custom string representation of the time range.

        Args:
            only_date (bool): Wheter to return only the date part of time range.
                Defaults to True.
        """
        if only_date:
            return [self._start_time.isoformat(sep='T').split('T')[0],
                    self._end_time.isoformat(sep='T').split('T')[0]]

        return [self._start_time.isoformat(sep='T'),
                self._end_time.isoformat(sep='T')]

    def convert_to_full_months(self):
        """
        Convert date to full months.
        For example, in the case of start time '2021-01-04' to '2021-01-01' or
        in the case of end time '2021-05-15' to '2021-05-31'.
        """
        self._start_time = self._start_time.replace(day=1)
        self._end_time = (self._end_time if self._end_time.is_month_end
                          else self._end_time + pd.offsets.MonthEnd())

    @classmethod
    def convert_time(cls,
                     datetime: Union[str, pd.Timestamp],
                     utc: bool = False):
        """Convert time to pandas Timestamp."""
        try:
            return pd.to_datetime(datetime, utc=utc)
        except Exception as error:
            raise ValueError(
                "Invalid input parameters -- must be convertable to pandas.TimeStamp") from error


class Geometry:
    """"Class for WKT type geometry.

        Args:
            geometry (Union[str, Polygon, MultiPolygon]): Geometry.
    """

    def __init__(self,
                 geometry: Union[str, Polygon, MultiPolygon]):

        if not isinstance(geometry, (Polygon, MultiPolygon)):
            geometry = self.convert_geometry(geometry)

        if not geometry.is_valid:
            raise ValueError(
                "Invalid geometry -- must be valid based on shapely's definition")

        self._geometry = geometry

    def __repr__(self):
        obj_name = f'<ddc_utility.{type(self).__name__}>'
        rep = f"{obj_name}\ngeometry: {self._geometry}\n"
        return rep

    @property
    def geometry(self):
        """Return geometry."""
        return self._geometry

    def to_string(self):
        """Return WKT string representation of the geometry."""
        return self._geometry.wkt

    @classmethod
    def convert_geometry(cls,
                         geometry: str):
        """Convert geometry to Shapely object."""
        try:
            geometry = shapely.from_wkt(geometry)
        except shapely.errors.GEOSException:
            geometry = MultiPolygon(shapely.from_geojson(geometry))
        except Exception as error:
            raise ValueError(
                "Invalid input parameters -- must be convertable to Shapely.geometry") from error

        if geometry.geom_type not in ['Polygon', 'MultiPolygon']:
            raise ValueError(
                "Invalid geometry type -- must be Polygon or MultiPolygon")

        return geometry


class IrrigationSchedule:
    """"Class for defining irrigation schedule.

        Args:
            date (Union[str, pd.Timestamp]): Irrigation date.
            amount (float): Amount of irrigated water in mm.
    """

    def __init__(self, date: Union[str, pd.Timestamp], amount: float):

        try:
            date = pd.to_datetime(date)
        except Exception as error:
            raise ValueError(
                "Invalid input parameters -- 'date' must be convertable to pandas.TimeStamp") from error

        try:
            amount = float(amount)
        except ValueError as error:
            raise ValueError(
                "Invalid input parameters -- 'amount must be convertable to float") from error

        self._date = pd.to_datetime(date)
        self._amount = float(amount)

    def __repr__(self):
        obj_name = f'<ddc_utility.{type(self).__name__}>'
        rep = f"{obj_name}\ndate: {self._date}\namount: {self._amount}\n"
        return rep

    @property
    def date(self):
        """Return geometry."""
        return self._date

    @property
    def amount(self):
        """Return geometry."""
        return self._amount

    def to_string(self, only_date=True):
        """Return the tuple string representation of the object."""
        if only_date:
            return (self._date.isoformat(sep='T').split('T')[0], self._amount)
        else:
            return (self._date.isoformat(sep='T'), self._amount)
