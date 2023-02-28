import requests
from newspaper import Article
import streamlit as st
import numpy as np
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
positivity = pipeline("text-classification",model='nlptown/bert-base-multilingual-uncased-sentiment',top_k=None)
emotion = pipeline("text-classification",model='bhadresh-savani/distilbert-base-uncased-emotion',top_k=None)

st.set_page_config(layout="wide", initial_sidebar_state = 'expanded')
st.header(":blue[News on topics relevant to BHL]")

if "para_state" not in st.session_state:
     st.session_state.para_state = False

with st.sidebar.form("Parameters"):

    option2 = st.selectbox("Articles on....", ("None", "Hydrogen Aviation", "Vertiports and Urban Air Mobility", "Sustainable Aviation Fuels", "Electric Aviation",
    "Aviation Green Finance"))
    option3 = st.selectbox("Do keyword search in...", ("None", 'title', 'content'))
    dict2 = {"None": "none",
             "Hydrogen Aviation": "(hydrogen AND engine AND plane) OR (hydrogen AND electric AND plane) OR (hydrogen-powered AND plane) OR (hydrogen-electric AND aircraft) OR (hydrogen AND aircraft) OR (hydrogen-electric AND flight) OR (hydrogen AND flight) OR (hydrogen AND plane)",
             "Sustainable Aviation Fuels": "sustainable AND aviation AND fuel",
             "Vertiports and Urban Air Mobility": "vertiports OR skyport OR evtol OR vtol OR (urban AND air AND mobility)",
             "Electric Aviation": "(electric AND aircraft) OR (electric AND plane) OR (electric AND flight) OR (electric AND aviation) OR (hybrid AND aircraft) OR (hybrid AND plane)",
             "Aviation Green Finance": "(aviation AND green AND finance and EU) OR (aviation AND green AND investment and EU)"
             }

    option4 = st.radio("Sort results by", ('Date published', 'Popularity'))
    dict4 = {'Date published':'publishedAt', 'Popularity': 'popularity'}

    option5 = st.selectbox("Include results from", ('a week ago', 'two weeks ago', 'a month ago'))
    dict5 = { 'a week ago': 7,
              'two weeks ago': 14,
              'a month ago': 31
             }

    option6 = st.radio("Conduct sentiment analysis of titles?", ('No', 'Yes'))

    submitted = st.form_submit_button("Search")

if submitted:
    st.session_state.search_state = True
    secret = st.secrets["key"]
    url = 'https://newsapi.org/v2/everything?'
    parameters = {
                'q': dict2[option2],  # query phrase
                'sortBy': dict4[option4],
                'from': date.today() - timedelta(days=dict5[option5]),
                'language': 'en',
                'searchIn': option3,
                'excludeDomains': "com.np,euractiv.com,khabarhub.com,rsc.org,yahoo.com,marketscreener.com,seekingalpha.com,moneycontrol.com,fool.com,prnewswire.co.uk,yankodesign.com,Gizmodo.jp,globalsecurity.org,atlantamagazine.com",
                'apiKey': secret  # your own API key
                }
    response = requests.get(url, params=parameters)
    response_json = response.json()
    #print(response_json)

    for n in range(0, response_json['totalResults']):
        st.subheader(response_json['articles'][n]['title'])
        st.caption(
            f":blue[{response_json['articles'][n]['publishedAt'][0:10]}//{response_json['articles'][n]['source']['name']}]")
        st.write("To read this article, click [here](%s)" % response_json['articles'][n]['url'],
                 unsafe_allow_html=False)
        if st.button("Generate AI-written summary", key=str(n)):
            art = Article(response_json['articles'][n]['url'])
            art.download()
            art.parse()
            art.nlp()
            sum2 = summarizer(art.text, min_length=200, max_length=300, do_sample=False)
            with st.expander("Summary"):
                st.markdown(sum2[0]['summary_text'])

    if option6 == 'Yes':
        df = pd.DataFrame()
        df2 = pd.DataFrame()
        col1, col2 = st.columns(2)
        with col1:
            for n in range(0, response_json['totalResults']):
                senti = positivity(response_json['articles'][n]['title'])
                index = []; data = []
                for i in range(0, 5):
                    index.append(int(senti[0][i]['label'][0]))
                    data.append(np.round(senti[0][i]['score'], 2))
                ser = pd.Series(data=data, index=index).sort_index(ascending=True)
                df = pd.concat([df,ser], axis=1)
            ser_mean = df.mean(axis=1)
            fig1 = px.pie(ser_mean, values=ser_mean.values, names=ser_mean.index,
                      title="Positivity score", color_discrete_sequence=px.colors.sequential.RdBu)
            fig1.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            for n in range(0, response_json['totalResults']):
                emo = emotion(response_json['articles'][n]['title'])
                index = [];data = []
                for i in range(0, 6):
                    index.append(emo[0][i]['label'])
                    data.append(np.round(emo[0][i]['score'], 2))
                ser2 = pd.Series(data=data, index=index).sort_index(ascending=True)
                df2 = pd.concat([df2, ser2], axis=1)
            ser_mean = df2.mean(axis=1)

            fig2 = px.pie(ser_mean, values=ser_mean.values, names=ser_mean.index,
                          title="Emotional components", color_discrete_sequence=px.colors.sequential.Viridis)
            fig2.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')
            st.plotly_chart(fig2, use_container_width=True)





