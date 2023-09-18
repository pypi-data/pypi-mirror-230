import requests
import json

from perdido.utils.xml import *


toponym = 'Lyon'


parameters = {'api_key': 'pythonLib', 'max_rows': 5, 'toponyms': ['Lyon'], 'sources':['geonames']}



result = requests.post('http://choucas.univ-pau.fr/PERDIDO/api/geocoding/', params=parameters)
print(result.text)

content_geojson = json.loads(result.text)['geojson']


toponyms = []
print(len(content_geojson['features']))
for feature in content_geojson['features']:

    lat = feature['geometry']['coordinates'][0]
    lng = feature['geometry']['coordinates'][1]
    name = feature['properties']['name']
    rend = feature['properties']['sourceName']
    source = feature['properties']['source']
    name = feature['properties']['name']
    type = 'ne'

    toponyms.append(Toponym(name, lat, lng, source, rend, type))


for t in toponyms:
    print(t)