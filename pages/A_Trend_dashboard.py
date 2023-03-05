import numpy as np
import pandas as pd
import requests
from datetime import date, timedelta
import plotly.express as px
from pytrends.request import TrendReq
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state='expanded')
st.title("Aviation trends dashboard")

@st.cache_resource
def load_model():
    from transformers import BertTokenizer, BertForSequenceClassification
    from transformers import pipeline
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    return(pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer,top_k=None))

senti = load_model()

choice = st.sidebar.radio("Choose to see trends for:", ("Sustainable Aviation Fuels", "Hydrogen Aviation", "Electric aviation", "eVTOL"))

dict = {"Sustainable Aviation Fuels": "sustainable aviation fuel",
        "Hydrogen Aviation": "hydrogen aircraft",
        "Electric aviation": "electric airplane",
        "eVTOL" : "eVTOL"
       }

st.subheader(":red[Google search trends]")
pytrends = TrendReq(hl='en-US', tz=0, timeout=(3.05, 27)) #tz=0 means timezone is UCT
pytrends.build_payload([dict[choice]], cat=0, timeframe='today 12-m')

# Interest trend over time
data_time = pytrends.interest_over_time()
data_time = data_time.reset_index()

# Top queries
data = pd.DataFrame(pytrends.related_queries())
data_top = data[dict[choice]]['top'][:5]

# Interest by country
by_region = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=False, inc_geo_code=False)
by_region = by_region[dict[choice]].nlargest(5)

# News scraping
dict2 = {    "Hydrogen Aviation": "(hydrogen AND engine AND plane) OR (hydrogen AND electric AND plane) OR (hydrogen-powered AND plane) OR (hydrogen-electric AND aircraft) OR (hydrogen AND aircraft) OR (hydrogen-electric AND flight) OR (hydrogen AND flight) OR (hydrogen AND plane)",
             "Sustainable Aviation Fuels": "sustainable AND aviation AND fuel",
             "eVTOL": "vertiports OR skyport OR evtol OR vtol OR (urban AND air AND mobility)",
             "Electric aviation": "(electric AND aircraft) OR (electric AND plane) OR (electric AND flight) OR (electric AND aviation) OR (hybrid AND aircraft) OR (hybrid AND plane)",
        }

secret = st.secrets["key"]
url = 'https://newsapi.org/v2/everything?'
parameters = {
                'q': dict2[choice],  # query phrase
                'sortBy': "publishedAt",
                'from': date.today() - timedelta(days=28),
                'language': 'en',
                'searchIn': "title",
                'excludeDomains': "docomo.ne.jp,com.np,euractiv.com,khabarhub.com,rsc.org,yahoo.com,marketscreener.com,seekingalpha.com,moneycontrol.com,fool.com,prnewswire.co.uk,yankodesign.com,Gizmodo.jp,globalsecurity.org,atlantamagazine.com",
                'apiKey': secret  # your own API key
                }
response = requests.get(url, params=parameters)
response_json = response.json()

df = pd.DataFrame(columns=["Title", "Date"])
for n in range(0, response_json['totalResults']):
        df.loc[n] = [response_json['articles'][n]['title'], response_json['articles'][n]['publishedAt'][0:10]]
df["Title"] = df["Title"].str.lower()
df = df.drop_duplicates(subset="Title")
df["Title"] = df["Title"].str.capitalize()
df = df.set_index(np.arange(0, len(df)))
count = df.groupby("Date").count()

#senti_score = SentimentIntensityAnalyzer()
df_senti = pd.DataFrame(columns=["Negative", "Neutral", "Positive"]) #columns=["Negative", "Neutral", "Positive","Compound"]

for i in range(0, len(df)):
    labels = []
    data = []
    score = senti(df.iloc[i]["Title"])
    for n in range(0, 3):
        labels.append(score[0][n]['label'])
        data.append(np.round(score[0][n]['score'], 2))
    ser = pd.Series(data=data, index=labels).sort_index(ascending=True)
    df_senti.loc[i] = ser.values

fig = px.line(data_time, x="date", y=dict[choice], title='Google search interest over time (past 12 months)')
st.plotly_chart(fig, use_container_width=True)

fig2, fig3 = st.columns(2)
with fig2:
        fig = px.bar(data_top, y="value",color="query", title='Top 5 related google search terms')
        fig.update_xaxes(visible=False, showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

with fig3:
        fig = px.bar(by_region, y= dict[choice],color=by_region.index,title='Countries with greatest interest')
        fig.update_xaxes(visible=False, showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

st.subheader(":red[News media trends]")
fig = px.bar(count, title='Number of news articles by date (past 28 days)')
st.plotly_chart(fig, use_container_width=True)

#color_discrete_map = {'Negative': '#EF553B', 'Positive': '#00CC96', 'Neutral': '#FFA15A'}
fig = px.bar(df_senti, x=df["Title"], y=["Negative", "Neutral", "Positive"],title='Sentiment analysis of News articles') #color_discrete_map=color_discrete_map)
fig.update_xaxes(visible=False, showticklabels=False)
st.plotly_chart(fig, use_container_width=True, theme="streamlit")

