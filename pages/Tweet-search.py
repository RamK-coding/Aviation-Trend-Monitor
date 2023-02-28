import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide", initial_sidebar_state = 'expanded')
st.header("Latest tweets on relevant topics")

bearer_token = os.environ.get("Token")

option = st.sidebar.selectbox("Select search term", ("none", "sustainable aviation fuel", "hydrogen aviation"))

def get_data(url,bt):
    headers = {'Authorization': "Bearer " + str(bt)}
    response = requests.get(url, headers=headers)
    response_data = response.json()
    return response_data

if option != "none":
    r = get_data(f'https://api.twitter.com/2/tweets/search/recent?query="{option}";max_results=30', bearer_token)
    df = pd.DataFrame(columns=["id", "Text"])
    print(r)
    for n in range(0, len(r['data'])):
        df.loc[n] = [r['data'][n]['id'], r['data'][n]['text']]
        df = df.drop_duplicates(subset='Text')
        df = df.set_index(np.arange(0, len(df)))
        #df["Text"] = df["Text"].map(lambda x: x.lstrip('RT '))
        #df = df.drop_duplicates(subset='Text')
    print(df)

    for n in range(0, len(df)):
        api = f"https://publish.twitter.com/oembed?url=https://twitter.com/edent/status/{df.loc[n]['id']}"
        #components.iframe(api, height=900, scrolling=True)
        res = requests.get(api)
        res = res.json()["html"]
        components.html(res, height=500, scrolling=True)











