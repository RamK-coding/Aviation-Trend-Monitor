import requests
from newspaper import Article
import streamlit as st
import numpy as np
from datetime import date, timedelta
import pandas as pd

st.set_page_config(layout="wide", initial_sidebar_state = 'expanded')
st.header(":blue[News on topics relevant to BHL]")

with st.sidebar.form("Parameters"):

    option2 = st.selectbox("Articles on....", ("None", "Hydrogen Aviation", "Vertiports and Urban Air Mobility", "Sustainable Aviation Fuels", "Electric Aviation",
    "Aviation Green Finance"))
    dict2 = {"None": "none",
             "Hydrogen Aviation": "(hydrogen AND engine AND plane) OR (hydrogen AND electric AND plane) OR (hydrogen-powered AND plane) OR (hydrogen-electric AND aircraft) OR (hydrogen AND aircraft) OR (hydrogen-electric AND flight) OR (hydrogen AND flight) OR (hydrogen AND plane)",
             "Sustainable Aviation Fuels": "sustainable AND aviation AND fuel",
             "Vertiports and Urban Air Mobility": "vertiports OR skyport OR evtol OR vtol OR (urban AND air AND mobility)",
             "Electric Aviation": "(electric AND aircraft) OR (electric AND plane) OR (electric AND flight) OR (electric AND aviation) OR (hybrid AND aircraft) OR (hybrid AND plane)",
             "Aviation Green Finance": "(aviation AND green AND finance and EU) OR (aviation AND green AND investment and EU)" #OR (aviation AND (greenwashing OR greenwash)) OR (plane AND (greenwashing OR greenwash)) OR ((flight OR flights) AND (greenwashing OR greenwash)"
             }

    option3 = st.selectbox("Do keyword search in...", ("None", 'title', 'content'))
    option4 = st.radio("Sort results by", ('Date published', 'Popularity'))
    dict4 = {'Date published':'publishedAt', 'Popularity': 'popularity'}

    option5 = st.selectbox("Include results from", ('a week ago', 'two weeks ago', 'a month ago'))
    dict5 = { 'a week ago': 7,
              'two weeks ago': 14,
              'a month ago': 28
             }

    submitted = st.form_submit_button("Search")

if submitted:

    secret = st.secrets["key"]
    url = 'https://newsapi.org/v2/everything?'
    parameters = {
                'q': dict2[option2],  # query phrase
                'sortBy': dict4[option4],
                'from': date.today() - timedelta(days=dict5[option5]),
                'language': 'en',
                'searchIn': option3,
                'excludeDomains': "docomo.ne.jp,com.np,euractiv.com,khabarhub.com,rsc.org,yahoo.com,marketscreener.com,seekingalpha.com,moneycontrol.com,fool.com,prnewswire.co.uk,yankodesign.com,Gizmodo.jp,globalsecurity.org,atlantamagazine.com",
                'apiKey': secret  # your own API key
                }
    response = requests.get(url, params=parameters)
    response_json = response.json()

    df = pd.DataFrame(columns=["Title","Link","Date","Source"])

    for n in range(0, response_json['totalResults']):
        df.loc[n] = [response_json['articles'][n]['title'], response_json['articles'][n]['url'],response_json['articles'][n]['publishedAt'][0:10],response_json['articles'][n]['source']['name']]
    df["Title"] = df["Title"].str.lower()
    df = df.drop_duplicates(subset="Title")
    df["Title"] = df["Title"].str.capitalize()
    df = df.set_index(np.arange(0, len(df)))

    for n in range(0,len(df)):
        st.subheader(df.iloc[n]['Title'])
        st.caption(f":blue[{df.iloc[n]['Date']}//{df.iloc[n]['Source']}]")
        st.write("To read this article, click [here](%s)" % df.iloc[n]['Link'],unsafe_allow_html=False)








