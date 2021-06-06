# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 12:01:27 2021

@author: aneesh
"""
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import requests
import pydeck as pdk
from datetime import datetime
import time


urls = { 
        "Past Hour" : "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        "Past Day" : "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
        "Past Week" : "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
        "Past Month" : "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
}


def load_data(data_url):
    
    response = requests.get(data_url).json()
    
    data = pd.DataFrame(columns=['title','place','magnitude','time','latitude',
                                 'longitude','depth','tsunami'])
    
    features = response['features']
    
    for feature in features:
        title = feature['properties']['title']
        place = feature['properties']['place']
        magnitude = feature['properties']['mag']
        time = feature['properties']['time']
        tsunami = feature['properties']['tsunami']
        longitude = feature['geometry']['coordinates'][0]
        latitude = feature['geometry']['coordinates'][1]
        depth = feature['geometry']['coordinates'][2]
        
        data = data.append({
            'title':title,
            'place':place,
            'time':int(time),
            'magnitude':magnitude,
            'tsunami':tsunami,
            'latitude':latitude,
            'longitude':longitude,
            'depth':depth
            }, ignore_index=True)
    
    data['magnitude'] = data['magnitude'].fillna(0).apply(lambda m:float(m))
    data['depth'] = data['depth'].fillna(0).apply(lambda d:float(d))
    data['time'] = data['time'].apply(lambda ts:datetime.utcfromtimestamp(ts/1000)\
                                      .strftime('%Y-%m-%d %H:%M:%S'))
    
    return data

def map(chart_placeholder, data, zoom):
    print("inside map")
    chart_placeholder.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": (np.max(data['latitude'])+np.min(data['latitude']))/2,
            "longitude": (np.max(data['longitude'])+np.min(data['longitude']))/2,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position=["longitude", "latitude"],
                pickable=True,
                opacity=0.6,
                stroked=True,
                filled=True,
                radius_units='pixels',
                radius_scale=100,
                radius_min_pixels=10,
                radius_max_pixels=100,
                line_width_min_pixels=1,
                get_radius= "magnitude",
                get_fill_color=[255, 0, 0],
                get_line_color=[0, 0, 0],
            ),
        ],
        tooltip={"text": "{title}\n{time}"}
    ))
    
    #return chart


def main():
    
    st.set_page_config(layout="wide")

    with st.sidebar:     
        st.title('Earthquake Visualizer')
        selected = st.selectbox(
            label="Select Frequency",
            options=list(urls.keys()),
            index=0
            )
    
    data = load_data(urls[selected])
    
    #data['mag_radius'] = data['magnitude'].apply(lambda m:m*10)
    chart_placeholder = st.empty()
    map(chart_placeholder, data, zoom=0.8)
    
    latest_quakes = data.sort_values(by=["time"], ascending=False)\
        .reset_index(drop=True)['title'][0:5]
    
    with st.sidebar:
        col1,col2 = st.beta_columns(2)
        
        with col1:
            st.subheader("Count: ")
        
        with col2:
            st.subheader(str(data.shape[0]))
            
        st.subheader("Latest quakes")        
        st.sidebar.table(pd.DataFrame(list(latest_quakes),columns=['locations']))
    

if __name__ == '__main__':
    main()