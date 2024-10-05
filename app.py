import streamlit as st
import pandas as pd
import folium
from folium import LayerControl, LatLngPopup
from streamlit_folium import st_folium
import os
import gpxpy
from app_fncs import prep_gpx, make_map, poi_fg, plot_layer_altair, parse_gpx # plot_cum_layer_altair, 

st.set_page_config(
    page_title="VAM content checker",
    page_icon="🥾",
    layout="wide")

st.title('🥾 App content checker')
st.write('## An app to help validate the data captured for each walk.')
#st.write('### Current Phase: Release 1 - Walks 1-10')

data_phase = st.selectbox('Select data capture phase... ', ('Release3', 'Release2', 'Release1'))

# get walks data
walks = pd.read_csv('WALKS.csv', usecols=['Name', 'ShortDescription', 'GeneralDescription', 'GeoJson', 'ShapeName', 'StartLocationLat', 'StartLocationLng', 'EndLocationLat', 'EndLocationLng', 'CoverImage', 
'Duration', 'Distance', 'Grading', 'Height', 'Ascent', 'Gear', 'Safety','CarparkGettingStart',	'WayMarked', 'DogsAllowed', 'Facilities', 'Accessible', 'AccessibleToilet', 'AccessibleTerrainDescription', 'NearestCarpark', 'ToEvolveTech', 'CoverImageFile'])
walks= walks.dropna(how='all')
# lets only use rows that have gpx files for now
#walks = walks.dropna(subset='GeoJson')
# and only rows that are from the selected data phase
walks = walks[walks.ToEvolveTech == data_phase]

# get POI data 
pois = pd.read_csv('POIs.csv')
pois = pois.dropna(how='all')
pois = pois.dropna(subset=['Latitude', 'Longitude'])

# get images info
images = pd.read_csv('IMAGES.csv')
images = images.dropna(how='all')

# set gpx folder location
gpx_dir = r"./gpx/"

# set images folder location
img_dir = r"./images"


# get list of walks from data
walklist  = list(walks.Name.unique())
selected_walk = st.selectbox(label='Select a walk from the dropdown list ...', options= walklist)
# create filtered dataframes
selected_walk_details = walks[walks['Name']==selected_walk]
selected_walk_pois = pois[pois['WALK_Name']==selected_walk]
selected_walk_imgs = images[images['Name']==selected_walk]


st.write('Short description:', '  \n', selected_walk_details.iloc[0,1])
st.write('General description:', '  \n', selected_walk_details.iloc[0,2])
st.dataframe(selected_walk_details)

# if os.path.isfile(os.path.join(img_dir, str(selected_walk_details.iloc[0,26]))):
#     # show cover image
#     st.image(os.path.join(img_dir, selected_walk_details.iloc[0,26]), caption='Cover Image')
# else:
#     st.write(f'could not find image at {os.path.join(img_dir, selected_walk_details.iloc[0,26])}')
#     st.write('No cover image for this walk')

st.write('Table of POIs on this walk. (Also shown as points on the map.)') 
st.dataframe(selected_walk_pois)


if len(str(selected_walk_details.GeoJson.iloc[0]))>1:
        gpx_file= os.path.join(gpx_dir, str(selected_walk_details.GeoJson.iloc[0]))
        if os.path.isfile(gpx_file):
            distances, elevations = parse_gpx(gpx_file)
            elev_plot_layer_altair = plot_layer_altair(distances, elevations)
            st.altair_chart(elev_plot_layer_altair)
            # elev_cum_plot_layer_altair = plot_cum_layer_altair(distances, elevations)
            # st.altair_chart(elev_cum_plot_layer_altair)

col = st.columns((2, 5, 2), gap='medium')

with col[0]:
    st.markdown('### Essential attributes')
    st.metric(label='Route shape', value=selected_walk_details.iloc[0, 4])
    st.metric(label='Duration', value=selected_walk_details.iloc[0, 10])
    st.metric(label='Distance', value=selected_walk_details.iloc[0, 11])
    st.metric(label='Grading', value=selected_walk_details.iloc[0, 12])
    st.metric(label='Waymarker', value=selected_walk_details.iloc[0, 18])
    st.metric(label='Dogs allowed', value=selected_walk_details.iloc[0, 19])
    st.write('**Nearest carpark:** ', selected_walk_details.iloc[0, 24])
    st.metric(label='Highest Point', value=selected_walk_details.iloc[0, 13])
    st.metric(label='Ascent', value=selected_walk_details.iloc[0, 14])
    st.metric(label='Facilities', value=selected_walk_details.iloc[0, 20])

with col[1]:
    if len(str(selected_walk_details.GeoJson.iloc[0]))>1:
        gpx_file= os.path.join(gpx_dir, str(selected_walk_details.GeoJson.iloc[0]))
        if os.path.isfile(gpx_file):
            gpx_pt_tpl, centre = prep_gpx(gpx_file)
            start_point = [selected_walk_details.iloc[0, 5], selected_walk_details.iloc[0, 6]]
            end_point = [selected_walk_details.iloc[0, 7], selected_walk_details.iloc[0, 8]]
            map = make_map(gpx_pt_tpl, centre, start_point, end_point)
            if selected_walk_pois.shape[0] > 0:
                pois = poi_fg(selected_walk_pois)
                map.add_child(pois)
                LayerControl().add_to(map)
                map.add_child(folium.LatLngPopup())
                #folium.LatLngPopup().add_to(map)

            st_data = st_folium(map, width='100%')
        else:
            st.write('## No map available as there is no gpx listed for this walk in the data capture sheet')

with col[2]:
    st.markdown('### Other attributes')
    st.write('**Gear**: ', selected_walk_details.iloc[0, 15])
    st.write('**Safety**: ', selected_walk_details.iloc[0, 16])
    st.write('**Car Park getting started:** ', selected_walk_details.iloc[0, 17]) 

if selected_walk_imgs.shape[0] > 0:
    st.write(f'There are {selected_walk_imgs.shape[0]} images for this walk:') 

    for id, row in selected_walk_imgs.iterrows():
        if os.path.isfile(os.path.join(img_dir, row['FILENAME'])):
            st.image(os.path.join(img_dir, row['FILENAME']), caption=row['Title'])
        else:
            st.write(f'could not find image at {os.path.join(img_dir, row["FILENAME"])}')
else:
    st.write('There are no images for this walk')
