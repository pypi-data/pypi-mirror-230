from django.test import RequestFactory, TestCase, Client
from django.contrib.auth.models import AnonymousUser, User

from measurements.writeapi import write
from measurements.models import Measure

LP_INVALID = """mymeas,mytag1=1 value=21 1463689680000000000"""

LP_VALID = """waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=21 1463689680000000000
waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=22 1463689690000000000
waves,parameter=AirPress_SL,sensor=WVP2,station=PTF value=23 1463689700000000000
"""

class WriteAPITest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_invalid_serie(self):
        request = self.factory.post('/measurements/api',
                                    data=LP_INVALID,
                                    content_type='application/octet-stream'
                                    )
        request.user = AnonymousUser()
        self.assertRaises(ValueError, write, request)

    def test_write(self):
        request = self.factory.post('/measurements/api',
                                    data=LP_VALID,
                                    content_type='application/octet-stream'
                                    )
        # TODO:
        request.user = AnonymousUser()
        write(request)
        self.assertTrue(Measure.objects.exists())

"""
create table measurements_duplicates as 
select id, m.serie_id, m.timestamp
from measurements_measure m, 
    (select serie_id, timestamp from measurements_measure 
            group by (serie_id, timestamp) having count(id) >1) as d 
where m.serie_id=d.serie_id and m.timestamp=d.timestamp;

-- test result --
select
mm.id as measure_id,
mm.serie_id,
ml.label AS location,
mst.source_id,
mst.network_id,
mp.code AS parameter,
mm."timestamp",
mm.value
from measurements_measure mm
LEFT JOIN measurements_serie ms ON mm.serie_id = ms.id
LEFT JOIN measurements_station mst ON ms.station_id = mst.id
LEFT JOIN measurements_location ml ON mst.location_id = ml.id
LEFT JOIN measurements_parameter mp ON ms.parameter_id = mp.id
where mm.id in (select id from measurements_duplicates) -- where date_part('year', timestamp)>=2020 )
order by mm.serie_id, timestamp, mm.id;

begin;
delete from measurements_measure
where id in 
(
select 
distinct on (mm.serie_id, timestamp) 
mm.id
from measurements_measure mm
where mm.id in (select id from measurements_duplicates)
order by mm.serie_id, timestamp, mm.id
);

commit;

"""