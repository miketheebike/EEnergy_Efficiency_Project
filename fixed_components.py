import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import numpy as np
import requests
#from requests_oauthlib import OAuth2Session
import csv
import altair as alt
import plotly.graph_objs as go
        
# Insert consent
def add_consent():
    st.session_state['consent'] = True

def consent_form():
    st.markdown("""
    By submitting the form below you agree to your data being used for research purposes. 
    """)
    agree = st.checkbox("I understand and consent.")
    if agree:
        st.markdown("You have consented. Select \"Next\" to start the survey.")
        st.button('Next', on_click=add_consent)

def personal_information():
    col1, _ = st.columns(2)
    with col1:
        st.text_input("Please, enter your full name and surname:", key = 'user_full_name')
        st.text_input("Please, enter your working title:", key = 'user_position')
        st.selectbox('Please, specify your professional category:', ('Policy implementer (EENergy consortium working package leaders)', 'Donor (European Commission)', 'Researcher', 'Sustainability Advisor', 'Entrepreneur/Firm Representative'), key="professional_category")
        st.number_input('Please, insert the years of experience you have working on energy efficiency:', min_value= 0, max_value= 70, key = 'years_of_experience')

def sustainability_advisors_question():
        if st.session_state['professional_category'] == 'Sustainability Advisor':
            st.write("") 
            st.write("")
            st.write("Please answer the following if you are a sustainability advisor.")
            col1, _ = st.columns(2)
            with col1:
                st.text_input("On average, how many hours did you spend working for each client in total?", key = "working_hours")
                st.text_input("How many firms they consult overall in a week (including firms outside of EEN)", key = "firms_consulted_pw")


def secrets_to_json():
    return {
        "folder_id": st.secrets["folder_id"],
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"],
        "universe_domain": st.secrets["universe_domain"],
        
    }

# EXAMPLE 

TITLE_INSTRUCTIONS = '''Instructions'''

SUBTITLE_INSTRUCTIONS = '''This example is designed to help you understand how to effectively respond to this survey. \\
For each question, you have a table with two columns. Please allocate probabilities based on the likelihood that you think a specific event will happen under the "Probability" column. The plot next to it will show the distribution of your answers. As an example, suppose we asked about your beliefs regarding tomorrow's maximum temperature in degrees Celsius in your city or town.'''

CAPTION_INSTRUCTIONS = '''In this case, your prediction indicates a 45\% chance of the maximum temperature reaching 26 degrees Celsius, 20\% chance of it reaching 26 degrees Celsius, and so on.'''

def instructions():

    st.subheader(TITLE_INSTRUCTIONS)
    st.write(SUBTITLE_INSTRUCTIONS)

    st.subheader("Temperature Forecast Tomorrow in Your City")
    st.write('_Please scroll on the table to see all available options._')

    #with data_container:
    table, plot = st.columns([0.4, 0.6], gap = "large")
    
    with table:
        # Create some example data as a Pandas DataFrame
        values_column = ['< 20'] + list(range(21, 30)) + ['> 30']
        zeros_column = [0 for _ in values_column]
        zeros_column[4:9] = [5, 15, 45, 20, 15]

        data = {'Temperature': values_column, 'Probability': zeros_column}
        df = pd.DataFrame(data)

        df['Temperature'] = df['Temperature'].astype('str')
    
        st.data_editor(df, use_container_width=True, hide_index=True, disabled=('Temperature', "Probability"))

    st.write(CAPTION_INSTRUCTIONS)

    with plot:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=values_column, 
            y=df['Probability'], 
            marker_color='rgba(50, 205, 50, 0.9)',  # A nice bright green
            marker_line_color='rgba(0, 128, 0, 1.0)',  # Dark green outline for contrast
            marker_line_width=2,  # Width of the bar outline
            text=[f"{p}" for p in df['Probability']],  # Adding percentage labels to bars
            textposition='auto',
            name='Probability'
        ))

        fig.update_layout(
            title={
                'text': "Probability distribution",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Expectation Range",
            yaxis_title="Probability (%)",
            yaxis=dict(
                range=[0, 100], 
                gridcolor='rgba(255, 255, 255, 0.2)',  # Light grid on dark background
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            xaxis=dict(
                tickangle=-45,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            font=dict(color='white'),  # White font color for readability
        )
        st.plotly_chart(fig)
    
def submit(): 
    st.session_state['submit'] = True
