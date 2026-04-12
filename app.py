import streamlit as st
import pandas as pd 
import plotly.express as px
import numpy as np
import time 

st.set_page_config(page_title="Smart Incubator Analytics", layout="wide")
st.sidebar.header("System Controls")
mode = st.sidebar.radio("Data Source:", ["Live ESP32 (MQTT)", "Simulation Mode"])
col1, col2 = st.columns(2)

if mode == "Simulation Mode":
   st.empty()

   #Mock Data for Temperature demonstration
   temp = 37.5 + np.random.uniform(-0.2,0.2)
   #Moch Data for Humidity
   hum = 55.0 + np.random.uniform(-1,1)
   with col1:
    st.metric(label="Current Temperature", value=f"{temp:.2f} °C", delta="Optimal")
   with col2:
    st.metric(label="Current Humidity", value=f"{hum:.1f}%", delta="-0.5%")

    #For the Trend Graph
    chart_data =pd.DataFrame(
    np.random.randn(20, 2) / [10,2] + [37.5, 55],
    columns=['Temperature', 'Humidity']
    )
    st.line_chart(chart_data)
    time.sleep(2)
   st.rerun()

else:
    st.warning("Waiting for MQTT connection from ESP32...")
