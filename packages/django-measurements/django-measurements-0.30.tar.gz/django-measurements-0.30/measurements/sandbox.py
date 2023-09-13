from django.core.management.base import BaseCommand

# from meteo.pgutils import load_data
from measurements.settings import SOURCE_AUTH
from measurements.sources.pessl import PesslAPI
from measurements.sources.mtt import MttAPI
from measurements.models import SourceType, Measure

a = MttAPI()
a.get_df(code='T0193')


from psqlextra.query import ConflictAction


ps = SourceType.objects.get(code='pessl')
for s in ps.station_set.all():
    keys = SOURCE_AUTH['pessl'][s.network.code]
    print(keys)
    pesslapi = PesslAPI(keys['public_key'],
                            keys['private_key'])
    df = pesslapi.get_df(s.code, 1000)
    print(df)



a = df[['HC Air temperature|avg']].copy()
a.reset_index(inplace=True)
a.columns = ['timestamp', 'value']
a['serie_id'] = 2

Measure.extra.on_conflict(['serie_id', 'timestamp', 'value'],
                          ConflictAction.UPDATE).bulk_insert(
    a.to_dict(orient='record'))

from measurements.sources.davis import DavisAPI

ds = DavisAPI()
a = ds.get_df('cantineferrari/ferrari1')


from django.conf import settings
from measurements.sources.elmed import ElmedAPI
elmed = ElmedAPI(None, settings.MEASUREMENTS_SOURCE_AUTH['elmed']['ferrari']['private_key'])
df = elmed.get_df(88)

from measurements.sources.ioc import IocAPI
ioc = IocAPI()
ioc.get_df("TR22")

# create IOC stations
from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType, Network
IOC_STATIONS = (
    ('Trieste', 'TR22'),
    ('Venice', 'VE19'),
    ('Ancona', 'AN15'),
    ('S. Benedetto Del Tronto', 'SB36'),
    ('Stari Grad', 'stari'),
    ('Vela Luka', 'vela'),
    ('Sobra', 'sobr'),
    ('Otranto', 'OT15'),
    ('Kerkyra, Corfu', 'corf'),
    ('Crotone', 'CR08'),
    ('Le Castella', 'lcst'),
    ('Itea', 'itea'),
    ('Panormos', 'pano'),
    ('Aigio', 'aigi'),
    ('Katakolo', 'kata'),
    # ('Kyparissia', 'kypa'),
)

network, crated = Network.objects.get_or_create(code='ioc', label='IOC')
source_type, created = SourceType.objects.get_or_create(code='ioc')

for slabel, scode in IOC_STATIONS:
    station, created = Station.objects.get_or_create(code=scode, label=slabel)
    station.source=source_type
    station.network = network
    station.save()

import pandas as pd
from measurements.sources.arso import ArsoAPI
from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType
arso = ArsoAPI()

ARSO_CODES = ['9350', '9400', '9410', '9420']

network, crated = Network.objects.get_or_create(code='arso', label='ARSO')
source_type, created = SourceType.objects.get_or_create(code='arso')
stations = arso.get_stations()
for scode in ARSO_CODES:
    slabel = stations.get(scode)
    station, created = Station.objects.get_or_create(code=scode, label=slabel)
    station.source=source_type
    station.network = network
    station.save()


from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType, Location
from measurements.sources.getit import GetitAPI
getit = GetitAPI()

data = getit.get_df("PTF - Piattaforma Acqua Alta", last=40)

CNR_STATIONS = {"PTF - Piattaforma Acqua Alta": "PTF - Piattaforma Acqua Alta"}
network, crated = Network.objects.get_or_create(code='cnr', label='CNR')
source_type, created = SourceType.objects.get_or_create(code='cnr')
for scode, slabel in CNR_STATIONS.items():
    station, created = Station.objects.get_or_create(code=scode, label=slabel)
    station.source=source_type
    station.network = network
    station.save()

# copy station code to station label
from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType, Location
for s in Station.objects.all():
    if s.label is None and s.code is not None:
        print(s)
        s.label = s.code.replace('_', ' ')
        s.save()


# copy station to location
from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType, Location
for s in Station.objects.all():
    if s.label is not None and s.location is None:
        print(s)
        l, created = Location.objects.get_or_create(label = s.label)
        s.location = l
        s.save()

# set empty network to rete telemaerografica
network, crated = Network.objects.get_or_create(code='cpsm', label='Rete Telemareografica')
for s in Station.objects.all():
    if s.network is None:
        s.network = network
        s.save()

"""
create view measurements_grafana_view
as SELECT mm."timestamp",
    mm.value,
    mm.value - ms.stats_mean as value_norm,
    ms.id as serie_id,
    ml.label AS location,
    ml.id AS location_id,
    st_x(ml.geo) AS longitude,
    st_y(ml.geo) AS latitude,
    mn.label as network,
    mn.id as network_id,
    mp.code AS parameter,
    mp.id AS parameter_id,
    ms.height
   FROM measurements_measure mm
     LEFT JOIN measurements_serie ms ON mm.serie_id = ms.id
     LEFT JOIN measurements_station mst ON ms.station_id = mst.id
     LEFT JOIN measurements_location ml ON mst.location_id = ml.id
     LEFT JOIN measurements_network mn ON mst.network_id = mn.id
     LEFT JOIN measurements_parameter mp ON ms.parameter_id = mp.id;
grant select on measurements_grafana_view to public;

create view measurements_grafana_wind_view
as 


select 
 timestamp,
 max(case when parameter = 'WSPD' then value end) as wspd,
 max(case when parameter = 'WDIR' then value end) as wdir,
 location
 from measurements_grafana_view
 where parameter in ('WSPD', 'WDIR')
 GROUP BY timestamp, location
  having wspd not null and wdir not null
;


SELECT mm."timestamp",
    mm.value,
    ml.label AS location,
    ml.id AS location_id,
    mp.code AS parameter,
    mp.id AS parameter_id
   FROM measurements_measure mm
     LEFT JOIN measurements_serie ms ON mm.serie_id = ms.id
     LEFT JOIN measurements_station mst ON ms.station_id = mst.id
     LEFT JOIN measurements_location ml ON mst.location_id = ml.id
     LEFT JOIN measurements_network mn ON mst.network_id = mn.id
     LEFT JOIN measurements_parameter mp ON ms.parameter_id = mp.id;
   WHERE mp.label IN ('WSPD', 'WDIR')
   GROUP BY mm."timestamp";

grant select on measurements_grafana_wind_view to public;
"""

# test for parse line protocol
from datetime import datetime
import pandas as pd
import io
from measurements.models import Measure, Station, Parameter, Sensor, Serie, SourceType, Network
TS_NS = 1000000000
dt = datetime.now()
d = dt - datetime(day=1, month=1, year=1970)
sec = int(d.total_seconds())
sec * TS_NS
#
data = """m,station=test,parameter=SLEV value=10 1573750497000000000
m,station=test,parameter=SLEV value=10 1573750498000000000
m,station=test,parameter=SLEV value=10 1573750499000000000
m,station=test,parameter=SLEV value=10 1573750500000000000
"""""
#
data = """
station,parameter,sensor,value,datetime
itea,SLEV,,10,1573754002000000000
itea,SLEV,,11,1573754002000000000
itea,SLEV,,12,1573754002000000000
itea,SLEV,,11,1573754002000000000
"""""

data = """
station,parameter,sensor,value,timestamp
itea,SLEV,,10,2019-11-14T17:00:00+01:00
itea,SLEV,,11,2019-11-14T17:10:00+01:00
itea,SLEV,,12,2019-11-14T17:20:00+01:00
itea,SLEV,,13,2019-11-14T17:30:00+01:00
itea,SLEV,,11,2019-11-14T17:40:00+01:00
"""""

import requests
iwsurl = "http://127.0.0.1:8000/measurements/writecsv"
r = requests.post(url=iwsurl,
                          data=data,
                          headers={'Content-Type': 'application/octet-stream'})

r.text
df.head()

# code to export - import old data
"""
drop table tmp_measures_arso;
-- select * from measurements_measure_view where network ='CNR';
-- create table tmp_measures_arso as select extract(epoch from timestamp) *1000000000  as timestamp, value, location, parameter from measurements_measure_view where network = 'CNR';
create table tmp_measures_arso 
as 
select extract(epoch from timestamp) *1000000000  as timestamp, value, location, parameter, ms.code as station 
from measurements_measure_view 
left join measurements_station ms on (location=ms.label)
where network = 'IOC';

-- Tržaški zaliv (Zarja) 
-- OB Piran (NIB) 9400
--  Koper - kapitanija  9350
-- alter table tmp_measures_arso add column station varchar;
alter table tmp_measures_arso add column sensor varchar;
-- update tmp_measures_arso set station = '9400' where location = 'OB Piran (NIB)';
-- update tmp_measures_arso set station = '9350' where location = 'Koper - kapitanija';
-- update tmp_measures_arso set station = 'PTF - Piattaforma Acqua Alta' where location = 'PTF - Piattaforma Acqua Alta';

COPY tmp_measures_arso(timestamp, value, station, parameter, sensor) TO '/tmp/tmp_measures_arso' DELIMITER ',' CSV HEADER;
"""

import pandas as pd
data = [
    [1, 'WSPD', 'unknown', 'PTF - Piattaforma Acqua Alta'],
    [2, 'WSPD', 'unknown', 'PTF - Piattaforma Acqua Alta'],
    [3, 'WSPD', 'unknown', 'PTF - Piattaforma Acqua Alta'],
    [1, 'WDIR', 'unknown', 'PTF - Piattaforma Acqua Alta']
]
df = pd.DataFrame(data, columns=['value', 'parameter', 'sensor', 'station'])
_df = df[['parameter', 'sensor', 'station']].drop_duplicates()
_