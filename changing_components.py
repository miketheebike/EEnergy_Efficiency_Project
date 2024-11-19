            
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import numpy as np
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from requests_oauthlib import OAuth2Session
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from fixed_components import *

import plotly.graph_objs as go

def initialize_session_state():
    # Add custom CSS to disable horizontal scrolling
    # Add custom CSS to prevent horizontal scrolling and reduce vertical spacing on mobile
    st.markdown(
        """
        <style>
            /* Prevent horizontal scrolling */
            body {
                overflow-x: hidden;
            }
            
            /* Ensure the main content doesn't exceed screen width */
            .main, .block-container {
                max-width: 100vw;
                overflow-x: hidden;
            }
    
            /* Adjust spacing for mobile */
            @media only screen and (max-width: 768px) {
                .block-container {
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                }
                .element-container {
                    margin-bottom: 0.5rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
        st.session_state['consent'] = False
        st.session_state['submit'] = False
        st.session_state['No answer'] = ''
        st.session_state['page'] = 0    
                

        
    if 'data' not in st.session_state:
        st.session_state['data'] = {
            'User Full Name': [],
            'User Working Position': [],
            'User Professional Category': [],
            'User Years of Experience': [],
            'Working Hours': [],
            'Minimum Effect Size Q1': [],
            'Minimum Effect Size Q2': [],    
            'Minimum Effect Size Q3': [],
            'Minimum Effect Size Q4': [],
            'Minimum Effect Size Q5': [],
            'Minimum Effect Size Q6': [],
            'Minimum Effect Size Q7': [],
            'Minimum Effect Size Q8': [],
            # 'Minimum Effect Size Q9': [],
            'Cost-Benefit Ratio': [],
            'Risk Aversion': [],
            # New keys for added questions
            'Years as Advisor': [],
            'Join Date EEN': [],
            'Expert or Generalist': [],
            'Work Dedication': [],
            'Firms Consulted Per Week': [],
            'Average Working Hours Per Client': [],
            'Number of Firms Advised on Sustainability': [],
            'Meeting Frequency': [],
            'Meeting Duration': [],
            'Topics Discussed': [],
            'Time Covered Rankings': [],
            'Meeting Effectiveness': [],
            'Advice Followed by Firms': [],
            'Reasons Firms Followed Advice': [],
            'Advice Not Followed by Firms': [],
            'Reasons Firms Did Not Follow Advice': [],
            'Expected Reduction in Energy Use': [],
            'Most Effective Measures': [],
            'Least Effective Measures': [],
            'Personal Hourly Fee': [],
            'Firm Hourly Fee': [],
            'Firm Hours Per Week': [],
            'Personal Hours Per Week': [],
            'Reasons for Following Advice': [],
            'Meeting Effectiveness': [],
            'Technologies Table': [],
            'Ranked Topics': []
        }
    
def safe_var(key):
    if key in st.session_state:
        return st.session_state[key]

def survey_title_subtitle(header_config):
    st.title(header_config['survey_title'])
    st.write(header_config['survey_description'])
            


def create_question(jsonfile_name):
    minor_value = str(jsonfile_name['minor_value'])
    min_value = jsonfile_name['min_value_graph']
    max_value = jsonfile_name['max_value_graph']
    interval = jsonfile_name['step_size_graph']
    major_value = str(jsonfile_name['major_value'])

    # Create a list of ranges based on the provided values
    x_axis = [minor_value] + [f"{round(i, 1)}% to {round((i + interval - 0.01), 2)}%" for i in np.arange(min_value, max_value, interval)] + [major_value]

    # TODO: find a way to remove it
    if jsonfile_name['min_value_graph'] == -1:
        x_axis.insert(6, "0%")
        x_axis[1] = '-0.99% to -0.81%'
        x_axis[7] = '0.01% to 0.19%'
    elif jsonfile_name['min_value_graph'] == -10:
        x_axis.insert(3, "0%")
        x_axis[5] = '0.01% to 4.99%'
    elif jsonfile_name['min_value_graph'] == 0:    
        x_axis[1] = '0.01% to 4.99%'

    y_axis = np.zeros(len(x_axis))

    # Create dataframe for bins and their values
    data = pd.DataFrame(list(zip(x_axis, y_axis)), columns=[jsonfile_name['column_1'], jsonfile_name['column_2']])
            

    # Display title and subtitle for the question
    st.subheader(jsonfile_name['title_question'])
    st.write(jsonfile_name['subtitle_question'])

    # Create a container for the data editor and other elements
    data_container = st.container()

    # Integrate the updated logic for displaying data editor and handling percentages
    with data_container:
        # Create table and plot layout
        table, plot = st.columns([0.4, 0.6], gap="large")

        with table:
            # Calculate the height based on the number of rows
            row_height = 35  # Adjust as necessary based on row size
            table_height = ((len(data)+1) * row_height) 
            # Display the data editor
            bins_grid = st.data_editor(data, 
                                       key=jsonfile_name['key'], 
                                       hide_index=True, 
                                       use_container_width=True, 
                                       disabled=[jsonfile_name['column_1']],
                                       height = table_height)

            # Calculate the remaining percentage to be allocated
            percentage_difference = round(100 - sum(bins_grid[jsonfile_name['column_2']]))

            # Helper function to display status message
            def display_message(message, color):
                styled_message = f'<b style="font-family:sans-serif; color:{color}; font-size: 20px; padding: 10px;">{message}</b>'
                st.markdown(styled_message, unsafe_allow_html=True)

            # Display appropriate message based on the percentage difference
            if percentage_difference > 0:
                display_message(f'You still have to allocate {percentage_difference}% probability.', 'Red')
            elif percentage_difference == 0:
                display_message('You have allocated all probabilities!', 'Green')
            else:
                display_message(f'You have inserted {abs(percentage_difference)}% more, please review your percentage distribution.', 'Red')

                        
    # with data_container:
    #     table, plot = st.columns([0.4, 0.6], gap="large")
    #     with table:
    #         bins_grid = st.data_editor(data, key= jsonfile_name['key'], hide_index=True, use_container_width=True, disabled=[jsonfile_name['column_1']])
    #         percentage_difference = 100 - sum(bins_grid[jsonfile_name['column_2']])

    #         # Display the counter
    #         if percentage_difference > 0:
    #             missing_prob = f'<b style="font-family:sans-serif; color:Red; font-size: 20px; ">You still have to allocate {percentage_difference}% probability.</b>'
    #             st.markdown(missing_prob, unsafe_allow_html=True)
                
    #         elif percentage_difference == 0:
    #             total_prob = f'<b style="font-family:sans-serif; color:Green; font-size: 20px; ">You have allocated all probabilities!</b>'
    #             st.markdown(total_prob, unsafe_allow_html=True)
    #         else:
    #             exceeding_prob = f'<b style="font-family:sans-serif; color:Red; font-size: 20px; ">You have inserted {abs(percentage_difference)}% more, please review your percentage distribution.</b>'
    #             st.markdown(exceeding_prob, unsafe_allow_html=True)
                      
        with plot:
            # Extract the updated values from the second column
            updated_values = bins_grid[jsonfile_name['column_2']]

            # Get rid of plot menu
            config = {'displayModeBar': False, "staticPlot": True }
                    
            # Plot the updated values as a bar plot
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=bins_grid[jsonfile_name['column_1']], 
                y=updated_values, 
                marker_color='rgba(50, 205, 50, 0.9)',  # A nice bright green
                marker_line_color='rgba(0, 128, 0, 1.0)',  # Dark green outline for contrast
                marker_line_width=2,  # Width of the bar outline
                text=[f"{p}" for p in bins_grid[jsonfile_name['column_2']]],  # Adding percentage labels to bars
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
            width = 350,
            height = 400
            )
            st.plotly_chart(fig, config = config ,use_container_width=True)

    return pd.DataFrame(bins_grid), percentage_difference, len(bins_grid)

def effect_size_question(jsonfile_name):
    col1, _ = st.columns(2)
    with col1:
        st.markdown(jsonfile_name['effect_size'])
        st.text_input("Please insert a number or skip if you are unsure.", key = jsonfile_name['num_input_question'])



def add_submission(updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df):

    updated_bins_list = [updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df]

    def restructure_df(df, i):
        transposed_df = df.transpose()
        transposed_df.columns =  [f'Q{i + 1}  {col}' for col in list(transposed_df.iloc[0])]
        transposed_df = transposed_df.iloc[1:]
        return transposed_df

    transposed_bins_list = []
    for i, df in enumerate(updated_bins_list):
        transposed_bins_list.append(restructure_df(df, i))

    # Concatenating transposed dataframes
    questions_df = pd.concat(transposed_bins_list, axis=1)

    # Resetting index if needed
    questions_df.reset_index(drop=True, inplace=True)

    # Update session state
    data = st.session_state['data']

    USER_FULL_NAME = 'User Full Name'
    USER_PROF_CATEGORY = 'User Professional Category'
    USER_POSITION = 'User Working Position'
    YEARS_OF_EXPERIENCE = 'User Years of Experience'
    WORKING_HOURS = 'Working Hours'
    MIN_EFF_SIZE_Q1 = 'Minimum Effect Size Q1'
    MIN_EFF_SIZE_Q2 = 'Minimum Effect Size Q2'
    MIN_EFF_SIZE_Q3 = 'Minimum Effect Size Q3'
    MIN_EFF_SIZE_Q4 = 'Minimum Effect Size Q4'
    MIN_EFF_SIZE_Q5 = 'Minimum Effect Size Q5'
    MIN_EFF_SIZE_Q6 = 'Minimum Effect Size Q6'
    MIN_EFF_SIZE_Q7 = 'Minimum Effect Size Q7'
    MIN_EFF_SIZE_Q8 = 'Minimum Effect Size Q8'
    #MIN_EFF_SIZE_Q9 = 'Minimum Effect Size Q9'
    #MIN_EFF_SIZE_Q10 = 'Minimum Effect Size Q10'
    COST_BENEFIT_RATIO = 'Cost-Benefit Ratio'
    RISK_AVERSION = 'Risk Aversion'
    # Define constants for the new fields
    YEARS_AS_ADVISOR = 'Years as Advisor'
    JOIN_DATE_EEN = 'Join Date EEN'
    EXPERT_OR_GENERALIST = 'Expert or Generalist'
    WORK_DEDICATION = 'Work Dedication'
    FIRMS_CONSULTED_PW = 'Firms Consulted Per Week'
    AVG_WORKING_HOURS_PER_CLIENT = 'Average Working Hours Per Client'
    NUM_FIRMS_ADVISED = 'Number of Firms Advised on Sustainability'
    MEETING_FREQUENCY = 'Meeting Frequency'
    MEETING_DURATION = 'Meeting Duration'
    TOPICS_DISCUSSED = 'Topics Discussed'
    TIME_COVERED_RANKINGS = 'Time Covered Rankings'
    MEETING_EFFECTIVENESS = 'Meeting Effectiveness'
    ADVICE_FOLLOWED = 'Advice Followed by Firms'
    REASONS_FOLLOWED = 'Reasons Firms Followed Advice'
    ADVICE_NOT_FOLLOWED = 'Advice Not Followed by Firms'
    REASONS_NOT_FOLLOWED = 'Reasons Firms Did Not Follow Advice'
    EXPECTED_REDUCTION = 'Expected Reduction in Energy Use'
    MOST_EFFECTIVE_MEASURES = 'Most Effective Measures'
    LEAST_EFFECTIVE_MEASURES = 'Least Effective Measures'
    PERSONAL_HOURLY_FEE = "Personal Hourly Fee"
    FIRM_HOURLY_FEE = "Firm Hourly Fee"
    FIRM_HOURS_PER_WEEK = "Firm Hours Per Week"
    PERSONAL_HOURS_PER_WEEK = "Personal Hours Per Week"
    REASONS_FOR_FOLLOWING = "Reasons for Following Advice"
    MEETING_EFFECTIVENESS = "Meeting Effectiveness"
    TECHNOLOGIES_TABLE = "Technologies Table"
    RANKED_TOPICS = "Ranked Topics"

    data[USER_FULL_NAME].append(safe_var('user_full_name'))
    data[USER_POSITION].append(safe_var('user_position'))
    data[USER_PROF_CATEGORY].append(safe_var('professional_category'))
    data[YEARS_OF_EXPERIENCE].append(safe_var('years_of_experience'))
    data[WORKING_HOURS].append(safe_var('working_hours'))
    data[MIN_EFF_SIZE_Q1].append(safe_var('num_input_question1'))
    data[MIN_EFF_SIZE_Q2].append(safe_var('num_input_question2'))
    data[MIN_EFF_SIZE_Q3].append(safe_var('num_input_question3'))
    data[MIN_EFF_SIZE_Q4].append(safe_var('num_input_question4'))
    data[MIN_EFF_SIZE_Q5].append(safe_var('num_input_question5'))
    data[MIN_EFF_SIZE_Q6].append(safe_var('num_input_question6'))
    data[MIN_EFF_SIZE_Q7].append(safe_var('num_input_question7'))
    data[MIN_EFF_SIZE_Q8].append(safe_var('num_input_question8'))
    #data[MIN_EFF_SIZE_Q9].append(safe_var('num_input_question9'))
    #data[MIN_EFF_SIZE_Q10].append(safe_var('num_input_question10'))
    data[COST_BENEFIT_RATIO].append(safe_var('cost_benefit'))
    data[RISK_AVERSION].append(safe_var('risk_aversion'))
    # Append the new fields
    data[YEARS_AS_ADVISOR].append(safe_var('years_as_advisor'))
    data[JOIN_DATE_EEN].append(safe_var('join_date_een'))
    data[EXPERT_OR_GENERALIST].append(safe_var('expert_or_generalist'))
    data[WORK_DEDICATION].append(safe_var('work_dedication'))
    data[FIRMS_CONSULTED_PW].append(safe_var('firms_consulted_pw'))
    data[AVG_WORKING_HOURS_PER_CLIENT].append(safe_var('working_hours'))
    data[NUM_FIRMS_ADVISED].append(safe_var('num_firms_advised'))
    data[MEETING_FREQUENCY].append(safe_var('meeting_frequency_advisors'))
    data[MEETING_DURATION].append(safe_var('meeting_duration_advisors'))
    data[TOPICS_DISCUSSED].append(safe_var('meeting_topics_advisors'))
    data[TIME_COVERED_RANKINGS].append(safe_var('time_covered_ranking'))
    data[MEETING_EFFECTIVENESS].append(safe_var('meeting_effectiveness_advisors'))
    data[ADVICE_FOLLOWED].append(safe_var('advice_followed_by_firms'))
    data[REASONS_FOLLOWED].append(safe_var('reasons_for_firms_following'))
    data[ADVICE_NOT_FOLLOWED].append(safe_var('advice_not_followed_by_firms'))
    data[REASONS_NOT_FOLLOWED].append(safe_var('reasons_firms_not_following'))
    data[EXPECTED_REDUCTION].append(safe_var('expected_reduction'))
    data[MOST_EFFECTIVE_MEASURES].append(safe_var('measures_effectiveness_most'))
    data[LEAST_EFFECTIVE_MEASURES].append(safe_var('measures_effectiveness_least'))
    data[PERSONAL_HOURLY_FEE].append(safe_var('personal_hourly_fee'))
    data[FIRM_HOURLY_FEE].append(safe_var('firm_hourly_fee'))
    data[FIRM_HOURS_PER_WEEK].append(safe_var('firm_hours_per_week'))
    data[PERSONAL_HOURS_PER_WEEK].append(safe_var('personal_hours_per_week'))
    data[REASONS_FOR_FOLLOWING].append(safe_var('reasons_for_firms_following'))
    data[MEETING_EFFECTIVENESS].append(safe_var('meeting_effectiveness_advisors'))
    #data[TECHNOLOGIES_TABLE].append(edited_df.to_dict())  # Save table as a dictionary
    #data[RANKED_TOPICS].append(ranked_topics)
    
    st.session_state['data'] = data
    
    session_state_df = pd.DataFrame(data)
    
    personal_data_df = session_state_df.iloc[:, :5]
    min_eff_df = session_state_df.iloc[:, 5:]

    concatenated_df = pd.concat([personal_data_df, questions_df.set_index(personal_data_df.index), min_eff_df.set_index(personal_data_df.index)], axis=1)
      
    st.session_state['submit'] = True
    
    #save data to google sheet
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_to_json(), scope)
    client = gspread.authorize(creds)
 
    sheet = client.open("EEnergy_Efficiency_Survey_Data").sheet1

    column_names_list = concatenated_df.columns.tolist()
    #column_names = sheet.append_row(column_names_list)

    sheet_row_update = sheet.append_rows(concatenated_df.values.tolist()) #.values.tolist())
    # Format the current datetime as a string
    current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #Navigate to the folder in Google Drive. Copy the Folder ID found in the URL. This is everything that comes after “folder/” in the URL.
    #backup_sheet = client.create(f'Backup_{data[USER_FULL_NAME]}_{current_time_str}', folder_id= secrets_to_json()['folder_id']).sheet1
    #backup_sheet = backup_sheet.append_rows(concatenated_df.values.tolist()) #(new_bins_df.iloc[:2].values.tolist())
    #backup_sheet.share('', perm_type = 'user', role = 'writer')

