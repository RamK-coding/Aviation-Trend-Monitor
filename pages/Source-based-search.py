from bs4 import BeautifulSoup
# BeautifulSoup allows us to parse the HTML content of a given URL and access its elements by identifying
# them with their tags and attributes. For this reason, we will use it to extract certain pieces of text
# from the websites.

import pandas as pd
from datetime import timedelta
import requests
from newspaper import Article
import streamlit as st

from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment = pipeline("text-classification",model='nlptown/bert-base-multilingual-uncased-sentiment',top_k=None)
# Transformers is a HuggingFace library of pretrained state-of-the-art models for natural
# language processing (NLP), computer vision, and audio and speech processing tasks.

# We will use the requests module to get the HTML code from the page and then navigate through it with the
# BeautifulSoup package.

r1 = requests.get("https://www.iata.org/en/pressroom/")
r2 = requests.get("https://www.transportenvironment.org/discover/")
r3 = requests.get("https://www.eurocontrol.int/newsroom")
r4 = requests.get("https://www.icao.int/newsroom/Pages/default.aspx")
r5 = requests.get("https://www.sesarju.eu/news")

content1 = r1.content
content2 = r2.content
content3 = r3.content
content4 = r4.content
content5 = r5.content

soup1 = BeautifulSoup(content1, "html5lib")
soup2 = BeautifulSoup(content2, "html5lib")
soup3 = BeautifulSoup(content3, "html5lib")
soup4 = BeautifulSoup(content4, "html5lib")
soup5 = BeautifulSoup(content5, "html5lib")
# "html5ib" is a parser library
# https://stackoverflow.com/questions/25714417/beautiful-soup-and-table-scraping-lxml-vs-html-parser
# details the advantages and disadvantages of different parsers

news1 = soup1.find_all("h3", class_="release-teaser-title")
news_links1 = soup1.find_all("a", class_="release-teaser")
news_dates1 = soup1.find_all("div", class_="release-teaser-date")
news2 = soup2.find_all("h3", class_="listing-item-header-title")
news_dates2 = soup2.find_all("time")
news3 = soup3.find_all("div", class_="field--promo-title field field--name-promo-title field--type-ds field--label-hidden field__item")
news_dates3 = soup3.find_all("time", class_="datetime")
news_links3 = soup3.find_all("a", class_="btn btn-outline-primary btn-sm btn btn-outline-primary btn-sm")
news4 = soup4.find_all("a", class_="newsTitle")
news_dates4 = soup4.find_all("div", id="NewsDate")
news5 = soup5.find_all("a", rel="bookmark")
news_links5 = soup5.find_all("div", class_="button_primary")
news_dates5 = soup5.find_all("div", class_="date")


titles = []
links = []
dates = []
sources = []

def source_id(len, src):
    for n in range (0, len):
        sources.append(src)

def title_links(news):
    for n in range(0, len(news)):
        title_n = news[n].get_text()
        title_n = title_n.strip()
        # .strip() added to remove the leading and trailing whitespace (in eurocontrol)
        titles.append(title_n)

title_links(news1)
for n in range(0, len(news_links1)):
    link_n = "https://www.iata.org/" + news_links1[n]['href']
    links.append(link_n)
for n in range(0, len(news_dates1)):
    date_n = news_dates1[n].get_text()
    dates.append(date_n)
source_id(len(news_links1),"iata.org")

title_links(news2)
for n in range(0, len(news2)):
    link_n = news2[n].find('a')['href']
    links.append(link_n)
for n in range(0, len(news_dates2)):
    date_n = news_dates2[n].get_text()
    dates.append(date_n)
source_id(len(news2),"transportenvironment.org")

title_links(news3)
for n in range(0, len(news3)):
    link_n = "https://www.eurocontrol.int/" + news_links3[n]["href"]
    links.append(link_n)
for n in range(0, len(news_dates3)):
    date_n = news_dates3[n].get_text()
    dates.append(date_n)
source_id(len(news3),"eurocontrol.int")

title_links(news4)
for n in range(0, len(news4)):
    link_n = news4[n]['href']
    links.append(link_n)
for n in range(0, len(news_dates4)):
    date_n = news_dates4[n].get_text()
    dates.append(date_n)
source_id(len(news4),"icao.int")

title_links(news5)
for n in range(0, len(news5)):
    link_n = "https://www.sesarju.eu/" + news_links5[n].find("a")["href"]
    links.append(link_n)
for n in range(0, len(news_dates5)):
    date_n = news_dates5[n].get_text()
    dates.append(date_n)
source_id(len(news4),"sesarju.eu")

df = pd.DataFrame()
df["Source"] = pd.Series(sources)
df["Title"] = pd.Series(titles)
df["Link"] = pd.Series(links)
df["Date"] = pd.to_datetime(pd.Series(dates), dayfirst=True)
df["Date"] = df["Date"].apply(lambda x: x.date()) #dropping time from datetime
df = df.sort_values("Date", ascending=False)
cutoff = df.iloc[0]['Date'] - timedelta(days=21)
df = df[df["Date"] > cutoff]

st.set_page_config(layout="wide", initial_sidebar_state = 'expanded')
st.header(":blue[Latest news articles from your favourite sources]")

option_list = df["Source"].unique().tolist()
option_list.insert(0, 'All')
option = st.sidebar.selectbox("Select news source", option_list)

if option == "All":
    for n in range(0, len(df)):

        st.subheader(df.iloc[n].Title)
        st.caption(f":blue[{df.iloc[n].Date}//{df.iloc[n].Source}]")
        st.write("To read this article, click [here](%s)" % df.iloc[n].Link, unsafe_allow_html=False)

        if st.button("Generate AI-written summary", key= str(n)):
            art = Article(df.iloc[n].Link)
            art.download()
            art.parse()
            art.nlp()
            sum2 = summarizer(art.text, min_length=200, max_length=300,do_sample=False)
            with st.expander("Summary"):
                st.markdown(sum2[0]['summary_text'])

else:
    df = df[df.Source==option]
    for n in range(0, len(df)):

        st.subheader(df.iloc[n].Title)
        st.caption(f":blue[{df.iloc[n].Date}//{df.iloc[n].Source}]")
        st.write("To read this article, click [here](%s)" % df.iloc[n].Link, unsafe_allow_html=False)

        if st.button("Generate AI-written summary", key= str(n)):
            art = Article(df.iloc[n].Link)
            art.download()
            art.parse()
            art.nlp()
            sum2 = summarizer(art.text, min_length=200, max_length=300, do_sample=False)
            with st.expander("Summary"):
                st.markdown(sum2[0]['summary_text'])







