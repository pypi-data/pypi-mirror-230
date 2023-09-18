import geopandas as gpd
import matplotlib.pyplot as plt
import os

# https://www.riannek.de/2022/gpx-to-geopandas/

folder = '/Users/lmoncla/Documents/Data/Corpus/Choucas/'

# Create empty GeoDataFrame
track = gpd.GeoDataFrame(columns=['name', 'geometry'], 
     geometry='geometry')


#for file in os.listdir(folder):
#    if file.endswith(('.gpx')):
#        try:
file = '1e_jour_de_champagny_le_haut_au_refuge_d.gpx'
gdf = gpd.read_file(folder + file, layer='tracks')
track = track.append(gdf[['name', 'geometry']])
#        except:
#            print("Error", file)

track.sort_values(by="name", inplace=True)
track.reset_index(inplace=True, drop=True)

# Save tracks as Shapefile
#track.to_file(folder + 'track.shp')

print(track.head())

# Simple plot
track.plot()


plt.savefig('track.jpg')