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


SECTION_ONE = '''Section 1: Background Information'''


def personal_information():
    st.subheader(SECTION_ONE)
    col1, _ = st.columns(2)
    with col1:
        st.text_input("Please, enter your full name:", key = 'user_full_name')
        st.text_input("Please, enter your working title:", key = 'user_position')
        st.selectbox('Please, specify your professional category:', ('Policy implementer (EENergy consortium working package leaders)', 'Donor (European Commission)', 'Researcher', 'Sustainability Advisor', 'Entrepreneur/Firm Representative'), key="professional_category")
        st.number_input(
    'Please, insert the years of experience you have working on energy efficiency:', 
    min_value=0.0, 
    step=0.5, 
    format="%.1f", 
    key='years_of_experience'
)

def entrepreneur_firm_representative_question():
    if st.session_state['professional_category'] == 'Entrepreneur/Firm Representative':
        st.write("")
        st.write("")
        st.write("Please answer the following if you are an Entrepreneur or Firm Representative.")
        col1, _ = st.columns(2)

        with col1:
            # Question 1: Number of advisors focusing on sustainability practices
            st.number_input("How many advisors help your firm with sustainability practices?", 
                            min_value=0, step=1, key="num_advisors")

            # Question 2: Frequency of meetings with advisors
            st.selectbox("How often do you meet with your advisors?", 
                         options=["Daily", "Weekly", "Monthly", "Quarterly", "Annually", "As needed"], key="meeting_frequency")

            # Question 3: Duration of typical meetings
            st.selectbox("How long are your typical meetings with them?", 
                         options=["Less than 30 minutes", "30-60 minutes", "1-2 hours", "More than 2 hours"], key="meeting_duration")

            # Question 4: Topics discussed in meetings
            st.text_area("What do you talk about in these meetings?", key="meeting_topics")

            # Question 5: Rating the helpfulness of meetings
            st.radio("How helpful are these meetings for your business?", 
                     options=["Very helpful", "Somewhat helpful", "Neutral", "Not very helpful", "Not helpful at all"], key="meeting_usefulness")

            # Question 6: Advice followed
            st.text_area("What specific advice did they give you that you decided to follow?", key="advice_followed")

            # Question 7: Reasons for following advice
            st.text_area("Why did you decide to follow this advice?", key="reasons_for_following")

            # Question 8: Advice not followed
            st.text_area("What specific advice did they give you that you decided not to follow?", key="advice_not_followed")

            # Question 9: Reasons for not following advice
            st.text_area("Why did you decide not to follow this advice? (For example: Financial costs, labor costs, or other reasons)", key="reasons_not_following")

# def sustainability_advisors_question():
#         if st.session_state['professional_category'] == 'Sustainability Advisor':
#             st.write("") 
#             st.write("")
#             st.write("Please answer the following if you are a sustainability advisor.")
#             col1, _ = st.columns(2)
#             with col1:
#                 st.text_input("On average, how many hours did you spend working for each client in total?", key = "working_hours")
#                 st.text_input("How many firms they consult overall in a week (including firms outside of EEN)", key = "firms_consulted_pw")


SECTION_TWO = '''Section 2: Understanding Your Work Context'''
SECTION_TWO_NOTES = '''Before we ask you about your expecataions, we would like to understand your work a bit better and will ask you about your last week. If the last week was not typical for your work (e.g., because you were on holidays), think of the week(s) before instead. The following questions will refer to this week, asking information that will allow us to better contextualize your expectations.'''

def sustainability_advisors_question():
    if st.session_state['professional_category'] == 'Sustainability Advisor':
        st.write("")
        st.write("")
        st.subheader(SECTION_TWO)
        # st.write(SECTION_TWO_NOTES)
        col1, _ = st.columns(2)

        with col1:
                # Advisor Background and Experience
                st.write("**Advisor Background and Experience**")
                st.number_input("How many years have you been working as an advisor on energy efficiency topics?", 
                    min_value=0.0, 
                    step=0.5, 
                    format="%.1f", 
                    key='years_as_advisor')
                st.date_input("In which year did you join EEN?", key="join_date_een")
                st.radio("Do you describe yourself as an energy efficiency expert, generalist, or other?", options=["Energy efficiency expert", "Generalist", "Other"], key="expert_or_generalist")
                st.selectbox("How do you usually find new clients or start working with them?", options=["Referrals", "Cold outreach", "Inbound inquiries", "Networking events", "Other"], key="client_acquisition")
                st.multiselect("When evaluating energy efficiency, what do you rely on most? (Select all that apply)", options=["Formal training", "Professional knowledge", "Experience", "Combination"], key="assessment_basis")
                st.selectbox("On average, what percentage of your work is related to energy efficiency topics?", options=["Less than 30%", "30-70%", "More than 70%"], key="work_dedication")
                
                # Workload and Client Interactions
                st.write("**Workload and Client Interactions**")
                st.write("For the following questions, please reflect on your typical work with firms in the past week. If the last week was unusual (e.g., due to vacation), please consider a typical week instead.")
                st.number_input("How many firms did you advise on energy efficiency topics in the past week (include all clients, not just those within EEN)?", min_value=0, step=1, key="firms_consulted_pw")
                st.number_input("On average, how many hours do you spend working with each client on a project or service?", min_value=0.0, step=0.5, key="working_hours")

                st.number_input("How many firms do you advise on sustainable development practices?", min_value=0, step=1, key="num_firms_advised")
                
                # Client Engagement and Meeting Effectiveness
                st.write("**Client Engagement and Meeting Effectiveness**")
                st.selectbox("How often do you meet with the firms you advise?", options=["Daily", "Weekly", "Monthly", "Quarterly", "Annually", "As needed"], key="meeting_frequency_advisors")
                st.selectbox("How long are your typical meetings with the firms you advise?", options=["Less than 30 minutes", "30-60 minutes", "1-2 hours", "More than 2 hours"], key="meeting_duration_advisors")
                # Updated question with multiple-choice selection
                st.multiselect(
                    "What topics do you usually discuss during your meetings with firms? (Select all that apply)", 
                    options=[
                        "Energy efficiency strategies",
                        "Sustainable development practices",
                        "Cost-saving measures",
                        "Regulatory compliance",
                        "Technology upgrades",
                        "Employee training",
                        "Environmental impact assessments",
                        "Other"
                    ], 
                    key="meeting_topics_advisors"
                )
                st.radio("Overall, how would you rate the usefulness of your meetings for helping firms improve their sustainability practices?", options=["Very useful", "Somewhat useful", "Neutral", "Not very useful", "Not useful at all"], key="meeting_usefulness_advisors")
                
                # Advice Given and Client Reactions
                st.write("**Advice Given and Client Reactions**")
                st.text_area("What advice have you given to firms that they have chosen to follow?", key="advice_followed_by_firms")
                st.text_area("Why do you think firms chose to follow your advice?", key="reasons_for_firms_following")
                st.text_area("What advice have you given to firms that they decided not to follow?", key="advice_not_followed_by_firms")
                st.text_area("Why do you think firms chose not to follow your advice? (e.g., financial costs, labor costs, other reasons)", key="reasons_firms_not_following")
                
                # Effectiveness of Energy Efficiency Measures and Expected Outcomes
                st.write("**Effectiveness and Expected Outcomes**")
                st.number_input("Of the 707 firms selected for the EENergy project, how many do you expect will achieve a reduction in energy use?", min_value=0, max_value=707, step=1, key="expected_reduction")
                st.text_area("In your opinion, what actions or solutions are most helpful for reducing a firm's energy use? (What might the success of an average firm depend on?)", key="measures_effectiveness_most")
                st.text_area("In your opinion, what actions or solutions are least helpful for reducing a firm's energy use?", key="measures_effectiveness_least")
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
