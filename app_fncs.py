import gpxpy
import folium
from folium import FeatureGroup, Marker

import geopandas as gpd
import pandas as pd

import altair as alt

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

# functions for gpx checks and elevation graph profile
# Function to parse the GPX file and extract elevation and distance
def parse_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Extract elevations and distances from the track points
    elevations = []
    distances = []
    total_distance = 0
    previous_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                elevations.append(point.elevation)
                if previous_point is not None:
                    distance = point.distance_3d(previous_point)
                    total_distance += distance / 1000  # Convert to kilometers
                distances.append(total_distance)
                previous_point = point
    
    return distances, elevations

# def get_total_ascent(data):
#     data['elev_diff'] = data['Elevation (m)'].diff()
#     ascents = data[data['elev_diff']>=0]
#     total_ascent = ascents.elev_diff.sum()
#     #print('ascent: ', total_ascent)
#     # descents = data[data['elev_diff']<=0]
#     # total_descent = descents.elev_diff.sum()*-1 
#     # print('descent: ', total_descent)
#     return total_ascent

# # smoothing
# def get_total_ascent(data, window=10):
#     # Apply rolling mean to smooth elevation data
#     data['smoothed_elevation'] = data['Elevation (m)'].rolling(window=window, min_periods=1).mean()

#     # Calculate the differences in smoothed elevation
#     data['elev_diff'] = data['smoothed_elevation'].diff()

#     # Keep only positive elevation differences (ascents)
#     ascents = data[data['elev_diff'] > 0]

#     # Sum up the ascent values
#     total_ascent = ascents['elev_diff'].sum()
#     return total_ascent

# # downsampling
# def get_total_ascent(data, sample_rate=10):
#     # Downsample the data by taking every Nth point
#     data_sampled = data.iloc[::sample_rate]

#     # Calculate the differences in elevation
#     data_sampled['elev_diff'] = data_sampled['Elevation (m)'].diff()

#     # Keep only positive elevation differences (ascents)
#     ascents = data_sampled[data_sampled['elev_diff'] > 0]

#     # Sum up the ascent values
#     total_ascent = ascents['elev_diff'].sum()
#     return total_ascent

# # apply minimum change threshold
# def get_total_ascent(data, threshold=0.0):
#     # Calculate the differences in elevation
#     data['elev_diff'] = data['Elevation (m)'].diff()

#     # Apply a threshold to ignore small elevation changes
#     data['elev_diff'] = data['elev_diff'].apply(lambda x: x if x > threshold else 0)

#     # Keep only positive elevation differences (ascents)
#     ascents = data[data['elev_diff'] > 0]

#     # Sum up the ascent values
#     total_ascent = ascents['elev_diff'].sum()
#     return total_ascent

# # smoothing and minimum threshold
# tricky to get parameters that work in both mountainous and flatter settings
# def get_total_ascent(data, window=1, threshold=1):
#     # Apply rolling mean to smooth elevation data
#     data['smoothed_elevation'] = data['Elevation (m)'].rolling(window=window, min_periods=1).mean()

#     # Calculate the differences in smoothed elevation
#     data['elev_diff'] = data['smoothed_elevation'].diff()

#     # Apply a threshold to ignore small elevation changes
#     data['elev_diff'] = data['elev_diff'].apply(lambda x: x if x > threshold else 0)

#     # Keep only positive elevation differences (ascents)
#     ascents = data[data['elev_diff'] > 0]

#     # Sum up the ascent values
#     total_ascent = ascents['elev_diff'].sum()
#     return total_ascent

# # vary threshold based on overall elevation profile
# def get_total_ascent(data):
#     # Calculate elevation range
#     elevation_range = data['Elevation (m)'].max() - data['Elevation (m)'].min()

#     # Adjust threshold dynamically based on elevation range
#     if elevation_range < 50:  # relatively flat
#         threshold = 1  # smaller threshold for flat terrain
#     else:  # hilly or mountainous
#         threshold = 5  # larger threshold for noisy, rugged terrain

#     # Calculate the elevation differences
#     data['elev_diff'] = data['Elevation (m)'].diff()

#     # Apply dynamic threshold to filter small changes
#     data['elev_diff'] = data['elev_diff'].apply(lambda x: x if x > threshold else 0)

#     # Keep only positive elevation differences (ascents)
#     ascents = data[data['elev_diff'] > 0]

#     # Sum up the ascent values
#     total_ascent = ascents['elev_diff'].sum()
#     return total_ascent

# vary downsample based on overall elevation profile
def get_total_ascent(data):
    # calculate length to node ratio
    len_node_ratio =  (data['Distance (km)'].max()*1000)/ data.shape[0]
    print(len_node_ratio)
    # Calculate elevation range
    #elevation_range = data['Elevation (m)'].max() - data['Elevation (m)'].min()

    # Adjust threshold dynamically based on elevation range
    if len_node_ratio < 28:  # relatively flat
        # Downsample the data by taking every Nth point
        #data = data.iloc[::30]
        #threshold = 1  # smaller threshold for flat terrain
        # Apply rolling mean to smooth elevation data
        data['smoothed_elevation'] = data['Elevation (m)'].rolling(window=30, min_periods=1).mean()
    else:  # hilly or mountainous
        #data = data.iloc[::25]
        # threshold = 5  # larger threshold for noisy, rugged terrain
        data['smoothed_elevation'] = data['Elevation (m)'].rolling(window=5, min_periods=1).mean()

    # Calculate the elevation differences
    data['elev_diff'] = data['smoothed_elevation'].diff()

    # Apply dynamic threshold to filter small changes
    #data['elev_diff'] = data['elev_diff'].apply(lambda x: x if x > threshold else 0)

    # Keep only positive elevation differences (ascents)
    ascents = data[data['elev_diff'] > 0]

    # Sum up the ascent values
    total_ascent = ascents['elev_diff'].sum()
    return total_ascent


def plot_layer_altair(distances, elevations):
    # Create a DataFrame for Altair
    data = pd.DataFrame({
        'Distance (km)': distances,
        'Elevation (m)': elevations
    })
    # get y min and max for axis scale
    y_min = data['Elevation (m)'].min()
    #print(y_min)
    y_max = data['Elevation (m)'].max() + 20

    total_ascent = round(get_total_ascent(data))
    text = alt.Chart().mark_text(text=f"Total Ascent: {total_ascent}m", 
                                 align='left',
                                 color='#052623',
                                 font='Myriad Pro Regular',
                                 ).encode(x=alt.datum(0), y=alt.datum(y_max))

    area_chart = alt.Chart(data).mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#8DC63F', offset=0), # brown 8c564b darkgreen 2ca02c rust green #bcbd22
                   alt.GradientStop(color='#ffffff', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0)
        #color="#052623" # no gradient, solid colour
        ).encode(
            alt.X('Distance (km)',
                  ),
            alt.Y('Elevation (m)', 
                  scale=alt.Scale(
                                  domain=[y_min, y_max]),
            ),
            opacity=alt.value(0.9)
            )
    

    line_chart_thick = alt.Chart(data).mark_line(
        ).encode(
            alt.X('Distance (km)'),
            alt.Y('Elevation (m)'),
            strokeWidth=alt.value(4),
            color=alt.value('#8DC63F')
        )
    
    line_chart_thin = alt.Chart(data).mark_line(
        ).encode(
            alt.X('Distance (km)'),
            alt.Y('Elevation (m)'),
            strokeWidth=alt.value(2),
            color=alt.value('#052623')
        )
    
    # chart =  area_chart + line_chart_thick + line_chart_thin + text
    chart =  line_chart_thick + line_chart_thin + text
    chart = chart.properties(
        width="container",
        height= 150
    ).configure_axis(
        grid=False,
        tickCount=5,
        titleFont='Myriad Pro Regular',
        titleFontSize=12,
        titleColor='#052623',
        labelFontSize=10,
        labelFont='Myriad Pro Regular', 
        labelColor= '#052623', 
        domainColor= '#052623'
    ).configure_title(
        fontSize=16,
        font='Branding SF Cmp',
        anchor='middle',
        color='#052623'
    ).configure_view(
       stroke=None,
    #    fill='#42A9C5',
    #    fillOpacity= 0.8
    )
    chart.save('graph.html')

    return chart

# def plot_cum_layer_altair(distances, elevations):
#     # Create a DataFrame for Altair
#     data = pd.DataFrame({
#         'Distance (km)': distances,
#         'Elevation (m)': elevations
#     })
#     #data['elev_diff'] = data['Elevation (m)'].diff()
#     #data['elev_cumulative'] = data['elev_diff'].cumsum()
#     data['elev_cumulative'] = data['Elevation (m)'].diff().cumsum()

#     # get y min and max for axis scale
#     y_min = data['elev_cumulative'].min()
#     y_max = data['elev_cumulative'].max() + 20
#     print(y_min, y_max)


#     total_ascent = round(get_total_ascent(data))
#     text = alt.Chart().mark_text(text=f"Total Ascent: {total_ascent}m", 
#                                  fontSize=12,
#                                  font='Myriad Pro Regular',
#                                  color='#052623'
#                                  ).encode(x=alt.datum(4), y=alt.datum(y_max))

#     area_chart = alt.Chart(data).mark_area(
#         #line={'color':'darkgreen'},
#         color=alt.Gradient(
#             gradient='linear',
#             stops=[alt.GradientStop(color='#8DC63F', offset=0), # brown 8c564b darkgreen 2ca02c rust green #bcbd22
#                    alt.GradientStop(color='#ffffff', offset=1)],
#             x1=1,
#             x2=1,
#             y1=1,
#             y2=0)
#         ).encode(
#             alt.X('Distance (km)'),
#             alt.Y('elev_cumulative', scale=alt.Scale(domainMin=y_min, #domain=[y_min, y_max], 
#                                                    zero=False)),
#             opacity=alt.value(0.9)
#             )
    

#     line_chart_white = alt.Chart(data).mark_line(
#         ).encode(
#             alt.X('Distance (km)'),
#             alt.Y('elev_cumulative'),
#             strokeWidth=alt.value(4),
#             color=alt.value('#FFFFFF')
#         )
    
#     line_chart_green = alt.Chart(data).mark_line(
#         ).encode(
#             alt.X('Distance (km)'),
#             alt.Y('elev_cumulative'),
#             strokeWidth=alt.value(2),
#             color=alt.value('#8DC63F')
#         )
    
#     chart =  area_chart + line_chart_white + line_chart_green + text
#     chart = chart.properties(
#         #title= None, 
#         width=1200,
#         height=150
#     ).configure_axis(
#         grid=False,
#         tickCount=5,
#         titleFont='Myriad Pro Regular',
#         titleFontSize=12,
#         titleColor='#052623',
#         labelFontSize=10,
#         labelFont='Myriad Pro Regular', # Eurostile Bold
#         labelColor= '#052623', #'#7f7f7f',
#         domainColor= '#052623'
#     ).configure_title(
#         fontSize=16,
#         font='Branding SF Cmp',
#         anchor='middle',
#         color='#052623'
#     ).configure_view(
#        stroke=None
#     )

#     return chart




