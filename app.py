import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import gpxpy
from app_fncs import prep_gpx, make_map

st.set_page_config(
    page_title="VAM content checker",
    page_icon="🥾",
    layout="wide")

st.title('🥾 VAM content checker')
st.write('## A first release of an app to help validate the data captured for each walk. ')
# get walks data
walks = pd.read_csv('WALKS.csv', usecols=['Name', 'GeneralDescription', 'GeoJson', 'ShapeName', 'StartLocationLat', 'StartLocationLng', 'EndLocationLat', 'EndLocationLng', 'CoverImage', 
'Duration', 'Distance', 'Grading', 'Height', 'Ascent', 'Gear', 'Safety','CarparkGettingStart',	'WayMarked', 'DogsAllowed', 'Facilities', 'Accessible', 'AccessibleToilet', 'AccessibleTerrainDescription', 'NearestCarpark'])
walks= walks.dropna(how='all')
# lets only use rows that have gpx files for now
walks = walks.dropna(subset='GeoJson')

# set gpx folder location
gpx_dir = r"./gpx/"


# get list of walks from data
walklist  = list(walks.Name.unique())
selected_walk = st.selectbox(label='Select a walk from the dropdown list ...', options= walklist)
# create filtered dataframe
selected_walk_details = walks[walks['Name']==selected_walk]

st.write('Walk description:', '  \n', selected_walk_details.iloc[0,1])
st.dataframe(selected_walk_details)

col = st.columns((2, 5, 2), gap='medium')

with col[0]:
    #st.markdown('### Walk attributes')
    st.metric(label='Route shape', value=selected_walk_details.iloc[0, 3])
    st.metric(label='Duration', value=selected_walk_details.iloc[0, 9])
    st.metric(label='Distance', value=selected_walk_details.iloc[0, 10])
    st.metric(label='Grading', value=selected_walk_details.iloc[0, 11])
    st.metric(label='Waymarker', value=selected_walk_details.iloc[0, 17])
    st.metric(label='Dogs allowed', value=selected_walk_details.iloc[0, 18])
    st.write('**Nearest carpark:** ', selected_walk_details.iloc[0, 23])
    st.metric(label='Highest Point', value=selected_walk_details.iloc[0, 12])
    st.metric(label='Ascent', value=selected_walk_details.iloc[0, 13])
    st.metric(label='Facilities', value=selected_walk_details.iloc[0, 19])

with col[1]:
    if len(selected_walk_details.GeoJson.iloc[0])>1:
        gpx_file= os.path.join(gpx_dir, selected_walk_details.GeoJson.iloc[0])
        gpx_pt_tpl, centre = prep_gpx(gpx_file)
        start_point = [selected_walk_details.iloc[0, 4], selected_walk_details.iloc[0, 5]]
        end_point = [selected_walk_details.iloc[0, 6], selected_walk_details.iloc[0, 7]]
        map = make_map(gpx_pt_tpl, centre, start_point, end_point)
        st_data = st_folium(map, width='100%')

with col[2]:
    st.write('**Gear**: ', selected_walk_details.iloc[0, 14])
    st.write('**Safety**: ', selected_walk_details.iloc[0, 15])
    st.write('**Car Park getting started:** ', selected_walk_details.iloc[0, 16])