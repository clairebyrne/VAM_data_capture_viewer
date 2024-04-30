import gpxpy
import folium
from folium import FeatureGroup, Marker

def prep_gpx(gpxData):
    '''adapted from 
    https://www.kaggle.com/code/paultimothymooney/overlay-gpx-route-on-osm-map-using-folium'''
    gpx_file = open(gpxData, 'r')
    gpx = gpxpy.parse(gpx_file)
    gpx_pt_tpl = []
    for track in gpx.tracks:
        for segment in track.segments:        
            for point in segment.points:
                gpx_pt_tpl.append(tuple([point.latitude, point.longitude]))
    latitude = sum(p[0] for p in gpx_pt_tpl)/len(gpx_pt_tpl)
    longitude = sum(p[1] for p in gpx_pt_tpl)/len(gpx_pt_tpl)
    centre = [latitude, longitude]

    return gpx_pt_tpl, centre


def make_map(gpx_pt_tpl, centre, start_point, end_point):
    myMap = folium.Map(location=centre, zoom_start=14)
    folium.PolyLine(gpx_pt_tpl, color="red", weight=2.5, opacity=1).add_to(myMap)
    folium.Marker(start_point, icon=folium.Icon(color='green'), popup="start point", tooltip="Start point").add_to(myMap)
    folium.Marker(end_point, icon=folium.Icon(color='red'), popup="end point", tooltip="end point").add_to(myMap)
    return myMap

def poi_fg(poi_df):
    pois = FeatureGroup(name='POIs')
    for id, row in poi_df.iterrows():
        pois.add_child(Marker(location=[row['Latitude'], row['Longitude']], popup=row['Title']))

    return pois