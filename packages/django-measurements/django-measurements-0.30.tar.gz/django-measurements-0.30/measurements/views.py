from django.http.response import JsonResponse
from measurements.models import Location
from django.db.models import Sum, Min, Max
from .utils import get_time, classify_fc
from django.apps import apps
from geojson import Feature, FeatureCollection, loads
from .models import Parameter, Serie, Measure, Station
from django.http import Http404


def locations_flatjson(request):
    return JsonResponse(Location.objects.get_flatjson(), safe=False)


def measure_geojson(request):
    metric = request.GET.get('metric', None)
    if metric is None:
        raise Http404("Metric not found")
    return JsonResponse(get_geojsonpg(metric))


def get_geojsonpg(metric):
    par, aggregate, time, cmap = metric.split('.')
    if aggregate == 'sum':
        AggregateMode = Sum
    elif aggregate == 'min':
        AggregateMode = Min
    elif aggregate == 'max':
        AggregateMode = Max

    start_time, end_time = get_time(time)

    parameter = Parameter.objects.get(code=par)

    qs = Measure.objects
    qs = qs.filter(serie__parameter=parameter)
    qs = qs.filter(timestamp__gte=start_time, timestamp__lte=end_time)

    if aggregate == 'last':
        results = qs.order_by('serie__station', 'serie__location', '-timestamp').distinct('serie__station', 'serie__location').values('serie__station', 'serie__location', 'value')
    else:
        results = qs.values('serie__station', 'serie__location').annotate(value=AggregateMode(
            'value'))  # .order_by('parameter', 'location', '-datetime').distinct('parameter', 'location')

    items = []

    for r in results:
        if r['serie__location'] is None:
            continue
        s = Station.objects.get(pk=r['serie__station'])
        l = Location.objects.get(pk=r['serie__location'])
        if l.geo is None:
            continue
        geometry = loads(l.geo.geojson)
        properties = {'value': r['value'],
                      'location': l.label,
                      'station': l.label}
        items.append(Feature(geometry=geometry.copy(), properties=properties))

    fc = FeatureCollection(items)
    classify_fc(fc, cmap=cmap, zeros=True)
    return fc

