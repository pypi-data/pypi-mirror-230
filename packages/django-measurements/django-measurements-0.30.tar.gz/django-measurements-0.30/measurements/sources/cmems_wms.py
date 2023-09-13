import logging
from datetime import date
import pandas as pd
from measurements.sources.base import BaseSource
from owslib.wms import WebMapService
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def response2df(response):
    res = BeautifulSoup(response.read(), 'xml')
    data = []
    for r in res.FeatureInfoResponse.findAll('FeatureInfo'):
        v = r.value.text
        t = r.time.text
        data.append([t, v])

    df = pd.DataFrame(data, columns=["time", 'value'])
    df.replace({'none': None}, inplace=True)
    df['value'] = df.value.astype(float)
    df['time'] = pd.to_datetime(df.time)
    df.set_index('time', inplace=True)
    return df


def get_timeindex(timepositions):
    dr = None
    for _t in timepositions:
        t = _t.strip()
        if '/' in t:
            start, end, freq = t.split('/')
            # print(pd.to_datetime(start))
            _dr = pd.date_range(start.strip(), end.strip(), freq='1D')
            # print(start, end, period)
        # positions.appen
        # print(t)
        else:
            try:
                _dr = pd.date_range(t, periods=1, freq='1D')
            except ValueError as err:
                logger.warning("Skip invalid time position: {0}".format(err))
                continue
        if dr is None:
            dr = _dr
        else:
            dr = dr.union(_dr)
    return dr


def align_time(time, time_index, tolerance='30d'):
    id = time_index.get_loc(time,
                            method='nearest',
                            tolerance=tolerance)
    return time_index[id]

# TODO: create view  SELECT DISTINCT l.label AS __text,
#     l.id AS __value
#    FROM measurements_station s
#      LEFT JOIN measurements_location l ON s.location_id = l.id
#   WHERE s.status::text = 'active'::text
#   ORDER BY l.label;

class CMEMSWmsDataSource(BaseSource):
    def __init__(self, url, version='1.3.0'):
        self.url = url

        self.wms = WebMapService(url,
                                 version=version)
        self.response = None
        self.df = None
        self._time_indexes = {}

    def get_timeindex(self, layer):
        if layer not in self._time_indexes:
            i = get_timeindex(self.wms[layer].timepositions)
            self._time_indexes[layer] = i
        return self._time_indexes.get(layer)

    def get_df(self, layer, point, reftime=None, elevation=None,
               timedelta=None, timegap=None):
        """
        Query the WMS data source using the GetFeatureInfo method. It supports Elevation and Time dimensions.

        :param layer: WMS layer
        :param point: lat/long 2D array
        :param reftime: WMS Time range (eg. '2020-01-01/2020-12-01') or single date when used in together with timedelta or timegap parameters (eg. 2020-12-01)
        :param elevation: specify an elevation/depth level. If None default elevation will be returned.
        :param timedelta: time delta in days
        :param timegap: time gap in days
        :return: DataFrame with a datetime index and a "value" column
        """
        if reftime is not None:
            _time = reftime
        else:
            _time = date.today().isoformat()
        if timedelta is not None:
            _end = pd.to_datetime(_time)
            if timegap is not None:
                _end = _end - pd.Timedelta(days=timegap)
            _start = _end - pd.Timedelta(days=timedelta)
            time_index = self.get_timeindex(layer)
            _start = align_time(_start, time_index)
            _end = align_time(_end, time_index)
            _time = "{}/{}".format(_start.isoformat()[:-6],
                                   _end.isoformat()[:-6])

        bbox = (point[0] - 0.1,
                point[1] - 0.1,
                point[0] + 0.1,
                point[1] + 0.1,
                )
        _options = {
            'layers': [layer],
            'srs': 'EPSG:4326',
            'bbox': bbox,
            'size': (3, 3),
            'format': 'image/jpeg',
            'query_layers': [layer],
            'info_format': "text/xml",
            'xy': (1, 1)
        }
        if _time is not None:
            _options['time'] = _time
        if elevation is not None:
            _options['elevation'] = elevation

        logger.debug("request {} {} {} {}".format(layer, point, _time, elevation))
        self.response = self.wms.getfeatureinfo(**_options)
        self.df = response2df(self.response)
        return self.df
