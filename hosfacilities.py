

import geopandas as gpd




import os




import googlemaps 
from datetime import datetime




from shapely.geometry import Point, Polygon


import pandas as pd
import matplotlib.pyplot as plt


# open file with hospital data


public_hospitals=pd.read_csv('C:\\Users\\bipin\\Documents\\public_hospital_list.csv')





public_hospitals['full_address'] = (public_hospitals['Address Line 1'] + ',' + public_hospitals['Address Line 2'] + ',' + public_hospitals['State']+',AUS').replace('\s+', ' ', regex=True)





gmaps = googlemaps.Client(key='xxyyyzzz')




public_hospitals['gcode'] = public_hospitals.full_address.apply(gmaps.geocode)





public_hospitals['lat'] = [g[0]['geometry']['location']['lat'] for g in public_hospitals.gcode]
public_hospitals['long'] = [g[0]['geometry']['location']['lng'] for g in public_hospitals.gcode]





public_hospitals['zipad']=list(zip(public_hospitals.long,public_hospitals.lat))





public_hospitals['geometry']=public_hospitals.zipad.apply(Point)





crs={'init':'epsg:4326'}





geo_df_all=gpd.GeoDataFrame(public_hospitals,crs=crs,geometry=public_hospitals['geometry'])




# Victoria electoral region shape file


vdf=gpd.read_file('./E_VIC21_region.shp')




vic=geo_df_all[geo_df_all.State=='VIC']





points_within = gpd.sjoin(vic, vdf, op='within')





pointsframe=pd.DataFrame(points_within)





hosno=pd.DataFrame(pd.DataFrame(points_within).groupby('E_div_numb',as_index=False)['Establishment ID'].count())




hosno=hosno.rename(columns={'Establishment ID':'hospital count'})





merged = vdf.merge(hosno, on='E_div_numb',how='left')





merged['hospital count']=merged['hospital count'].fillna(0)





import plotly.express as px





mjson=merged.to_json()





fig = px.choropleth_mapbox(merged, geojson=json.loads(mjson), locations=merged.Sortname, color='hospital count',
                           featureidkey='properties.Sortname',
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           opacity=1,
                           zoom=5, center = {"lat": -37.85, "lon": 145.35},
                           labels={'hospital count':'hoscnt','Electoral division':'Elect_div'}
                          )
fig.update_geos(fitbounds="locations", visible=False)
fig.show()


