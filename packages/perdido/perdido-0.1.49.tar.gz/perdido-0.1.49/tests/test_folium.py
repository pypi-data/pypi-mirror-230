import folium
import json
import random


#colors = ['lightgray', 'pink', 'darkred', 'red', 'lightblue', 'darkblue', 'darkpurple', 'green', 'blue', 'lightgreen', 'lightred', 'gray', 'cadetblue', 'orange', 'purple', 'darkgreen', 'black', 'beige', 'white']


colors = ['blue','red','green','orange','purple', 'pink','gray','black', 'beige', 'white','darkblue', 'darkred', 'darkgreen','darkpurple','cadetblue', 'lightgray', 'lightblue',  'lightred', 'lightgreen']

# Charger les données à partir du fichier JSON
#with open('data.json') as f:
#    data = json.load(f)

d = {'type': 'FeatureCollection',
 'features': [{'type': 'Feature',
   'geometry': {'type': 'Point', 'coordinates': [4.832011, 45.757814]},
   'properties': {'id': 'en.1',
    'name': 'Lyon',
    'sourceName': 'Lyon, Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, France',
    'type': 'administrative',
    'country': 'France',
    'source': 'nominatim'}},
  {'type': 'Feature',
   'geometry': {'type': 'Point', 'coordinates': [4.832432, 45.757656]},
   'properties': {'id': 'en.3',
    'name': 'place Bellecour',
    'sourceName': 'Place Bellecour, Lyon 2e Arrondissement, Lyon, Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, 69002, France',
    'type': 'pedestrian',
    'country': 'France',
    'source': 'nominatim'}},
  {'type': 'Feature',
   'geometry': {'type': 'Point', 'coordinates': [4.831847, 45.759798]},
   'properties': {'id': 'en.7',
    'name': 'place des Célestins',
    'sourceName': 'Place des Célestins, Lyon 2e Arrondissement, Lyon, Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, 69002, France',
    'type': 'square',
    'country': 'France',
    'source': 'nominatim'}},
  {'type': 'Feature',
   'geometry': {'type': 'Point', 'coordinates': [4.833538, 45.760509]},
   'properties': {'id': 'en.11',
    'name': 'fontaine des Jacobins',
    'sourceName': 'Fontaine des Jacobins, Place des Jacobins, Lyon 2e Arrondissement, Lyon, Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, 69002, France',
    'type': 'fountain',
    'country': 'France',
    'source': 'nominatim'}},
  {'type': 'Feature',
   'geometry': {'type': 'Point', 'coordinates': [4.828689, 45.759471]},
   'properties': {'id': 'en.15',
    'name': 'pont Bonaparte',
    'sourceName': 'Pont Bonaparte, Lyon 2e Arrondissement, Lyon, Métropole de Lyon, Rhône, Auvergne-Rhône-Alpes, France métropolitaine, 69002, France',
    'type': 'bridge',
    'country': 'France',
    'source': 'nominatim'}}]}

#data = json.dumps(d)

# Créer la carte
m = folium.Map(location=[45.757656, 4.832432], zoom_start=13)

# Créer un groupe de marqueurs
marker_group = folium.FeatureGroup()




# Dictionnaire pour stocker les associations nom-couleur
name_colors = {}
cpt_color = 0
# Ajouter des marqueurs à partir des données JSON
for point in d['features']:
    name = point['properties']['name']
    # Récupérer la couleur associée au nom
    color = name_colors.get(name)
    # Si le nom n'est pas encore dans le dictionnaire, générer une couleur aléatoire
    if color is None:
          color = colors[cpt_color]
          cpt_color+=1
          #color = '#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
          name_colors[name] = color
    # Ajouter un marqueur à la carte
    marker = folium.Marker(
        location=[point['geometry']['coordinates'][1], point['geometry']['coordinates'][0]],
        icon=folium.Icon(color=color, icon='location-pin'),
        popup='Name: {}<br>Source: {}<br>Type: {}'.format(name, point['properties']['source'], point['properties']['type'])
     
    )
    marker_group.add_child(marker)

    print(color)

# Ajouter le groupe de marqueurs à la carte
m.add_child(marker_group)

# Afficher la carte
m.save("map.html")
