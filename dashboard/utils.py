import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path="cleandata.csv"):
    return pd.read_csv(path)
