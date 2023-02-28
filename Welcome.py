import streamlit as st
import toml

st.set_page_config(layout="wide", initial_sidebar_state='expanded')
st.image("BHL.png")
st.title("Welcome to the Aviation Trend Monitor!")
st.caption(":blue[Created by Ram Kamath :sunglasses:]")

#****Creating a TOML file****
#data = { "key": ""
#       }

#toml_string = toml.dumps(data)  # Output to a string
#output_file_name = "output.toml"
#with open(output_file_name, "w") as toml_file:
#    toml.dump(data, toml_file)