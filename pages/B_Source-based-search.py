from bs4 import BeautifulSoup
# BeautifulSoup allows us to parse the HTML content of a given URL and access its elements by identifying
# them with their tags and attributes. For this reason, we will use it to extract certain pieces of text
# from the websites.
import pandas as pd
from datetime import timedelta
import requests
import streamlit as st

# We will use the requests module to get the HTML code from the page and then navigate through it with the
# BeautifulSoup package.

def source_id(len, src):
    for n in range (0, len):
        sources.append(src)

def title_links(news):
    for n in range(0, len(news)):
        title_n = news[n].get_text()
        title_n = title_n.strip()
        # .strip() added to remove the leading and trailing whitespace (in eurocontrol)
        titles.append(title_n)

def dframe(sources, titles, links, dates):
    df = pd.DataFrame()
    df["Source"] = pd.Series(sources)
    df["Title"] = pd.Series(titles)
    df["Link"] = pd.Series(links)
    df["Date"] = pd.to_datetime(pd.Series(dates), dayfirst=True)
    df["Date"] = df["Date"].apply(lambda x: x.date())  # dropping time from datetime
    df = df.sort_values("Date", ascending=False)
    cutoff = df.iloc[0]['Date'] - timedelta(days=21)
    df = df[df["Date"] > cutoff]
    return(df)

def dframe_nodate(sources, titles, links):
    df = pd.DataFrame()
    df["Source"] = pd.Series(sources)
    df["Title"] = pd.Series(titles)
    df["Link"] = pd.Series(links)
    return(df)

def display(df):
    for n in range(0, len(df)):
        st.subheader(df.iloc[n].Title)
        st.caption(f":blue[{df.iloc[n].Date}//{df.iloc[n].Source}]")
        st.write("To read this article, click [here](%s)" % df.iloc[n].Link, unsafe_allow_html=False)

def display_nodate(df):
    for n in range(0, len(df)):
        st.subheader(df.iloc[n].Title)
        st.caption(f":blue[{df.iloc[n].Source}]")
        st.write("To read this article, click [here](%s)" % df.iloc[n].Link, unsafe_allow_html=False)

st.set_page_config(layout="wide", initial_sidebar_state = 'expanded')
st.header(":blue[Latest news articles from your favourite sources]")

with st.form("Parameters"):
    source = st.selectbox("Articles from....", ("None", "IATA", "Sesar", "Transport Environment","Eurocontrol","ICAO", "TNMT", "All"))
    if st.form_submit_button("Search"):
        titles = []
        links = []
        dates = []
        sources = []

        if source == "None":
            st.error("No news source selected")

        elif source == "TNMT":
            r6 = requests.get("https://tnmt.com/articles/")
            content6 = r6.content
            soup6 = BeautifulSoup(content6, "html5lib")
            news6 = soup6.find_all("h3", class_="teaser__hl")
            news_links6 = soup6.find_all("a", class_="teaser__link")
            title_links(news6)
            for n in range(0, len(news_links6)):
                link_n = news_links6[n]['href']
                links.append(link_n)
            source_id(len(news_links6), "tnmt.com")
            df = dframe_nodate(sources, titles, links)
            display_nodate(df)

        elif source == "IATA":
            r1 = requests.get("https://www.iata.org/en/pressroom/")
            content1 = r1.content
            soup1 = BeautifulSoup(content1, "html5lib")
            # "html5ib" is a parser library
            # https://stackoverflow.com/questions/25714417/beautiful-soup-and-table-scraping-lxml-vs-html-parser
            # details the advantages and disadvantages of different parsers
            news1 = soup1.find_all("h3", class_="release-teaser-title")
            news_links1 = soup1.find_all("a", class_="release-teaser")
            news_dates1 = soup1.find_all("div", class_="release-teaser-date")
            title_links(news1)
            for n in range(0, len(news_links1)):
                link_n = "https://www.iata.org/" + news_links1[n]['href']
                links.append(link_n)
            for n in range(0, len(news_dates1)):
                date_n = news_dates1[n].get_text()
                dates.append(date_n)
            source_id(len(news_links1), "iata.org")
            df = dframe(sources, titles, links, dates)
            display(df)

        elif source == "Transport Environment":
            r2 = requests.get("https://www.transportenvironment.org/discover/")
            content2 = r2.content
            soup2 = BeautifulSoup(content2, "html5lib")
            news2 = soup2.find_all("h3", class_="listing-item-header-title")
            news_dates2 = soup2.find_all("time")
            title_links(news2)
            for n in range(0, len(news2)):
                link_n = news2[n].find('a')['href']
                links.append(link_n)
            for n in range(0, len(news_dates2)):
                date_n = news_dates2[n].get_text()
                dates.append(date_n)
            source_id(len(news2), "transportenvironment.org")
            df = dframe(sources, titles, links, dates)
            display(df)

        elif source == "Eurocontrol":
            r3 = requests.get("https://www.eurocontrol.int/newsroom")
            content3 = r3.content
            soup3 = BeautifulSoup(content3, "html5lib")
            news3 = soup3.find_all("div", class_="field--promo-title field field--name-promo-title field--type-ds field--label-hidden field__item")
            news_dates3 = soup3.find_all("time", class_="datetime")
            news_links3 = soup3.find_all("a", class_="btn btn-outline-primary btn-sm btn btn-outline-primary btn-sm")
            title_links(news3)
            for n in range(0, len(news3)):
                link_n = "https://www.eurocontrol.int/" + news_links3[n]["href"]
                links.append(link_n)
            for n in range(0, len(news_dates3)):
                date_n = news_dates3[n].get_text()
                dates.append(date_n)
            source_id(len(news3), "eurocontrol.int")
            df = dframe(sources, titles, links, dates)
            display(df)

        elif source == "ICAO":
            r4 = requests.get("https://www.icao.int/newsroom/Pages/default.aspx")
            content4 = r4.content
            soup4 = BeautifulSoup(content4, "html5lib")
            news4 = soup4.find_all("a", class_="newsTitle")
            news_dates4 = soup4.find_all("div", id="NewsDate")
            title_links(news4)
            for n in range(0, len(news4)):
                link_n = news4[n]['href']
                links.append(link_n)
            for n in range(0, len(news_dates4)):
                date_n = news_dates4[n].get_text()
                dates.append(date_n)
            source_id(len(news4), "icao.int")
            df = dframe(sources, titles, links, dates)
            display(df)

        elif source == "Sesar":
            r5 = requests.get("https://www.sesarju.eu/news")
            content5 = r5.content
            soup5 = BeautifulSoup(content5, "html5lib")
            news5 = soup5.find_all("a", rel="bookmark")
            news_links5 = soup5.find_all("div", class_="button_primary")
            news_dates5 = soup5.find_all("div", class_="date")
            title_links(news5)
            for n in range(0, len(news5)):
                link_n = "https://www.sesarju.eu/" + news_links5[n].find("a")["href"]
                links.append(link_n)
            for n in range(0, len(news_dates5)):
                date_n = news_dates5[n].get_text()
                dates.append(date_n)
            source_id(len(news5), "sesarju.eu")
            df = dframe(sources, titles, links, dates)
            display(df)













