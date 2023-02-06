import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(layout = 'wide')

# use a temporary local file path until this is uploaded to the server
data = pd.read_csv('summaryChairsBasic.csv')
data['Date'] = pd.to_datetime(data['Start Time'], utc = True)
data['Date'] = data['Date'].dt.date

# create a session state for the schedule_appointment variable
if 'schedule_appointment' not in st.session_state:
    st.session_state.schedule_appointment = False

# createa a bold header for the steamlit landing page that welcomes the user to the updated scheduler
st.title('Welcome to the updated scheduler for WeInfuse')

# create a button that confirms the user wants to schedule a new appointment
st.subheader('Please click the box below to schedule a new appointment')
schedule_appointment = st.button('Schedule Appointment')
if schedule_appointment:
    st.session_state.schedule_appointment = True

# create a conditional statement that will only run if the user clicks the schedule_appointment button
if st.session_state.schedule_appointment:

    # create a user input that allows the user to enter the patient's name as (First Name Last Name)
    #patient_name = st.text_input('Enter the patient first and last name')

    # create a user input that allows the user to enter the patient's unique identifier
    #patient_id = st.text_input('Enter the patient unique identifier (IV#####)')

    # create a user input that allows the user to enter the patient's date of birth
    #patient_dob = st.date_input('Confirm the patient\'s date of birth. You can type it in or select from the calendar. Please use yyyy/mm/dd format.', min_value = datetime.date(year = 1900, month = 1, day = 1))

    # create a user input that allows the user to enter the patient's phone number
    #patient_phone = st.text_input('Enter the patient contact number (xxx-xxx-xxxx)')

    # create a list of locations from the location column in the chairs.csv file
    locations = data['LocationName'].unique()

    # create a dropdown menu that allows the user to select the location the patient is being seen at
    location = st.selectbox('Select the location the patient is being seen at', locations)

    # create a dictionary from two columns of the data dataframe where the key value is the location column and the value is the location ID column
    location_ids = dict(zip(data['LocationName'], data['LocationID']))
    
    # create a variable that will select the location ID based on the location selected by the user
    location_id = location_ids[location]

    # create a location based dataframe that only contains the location ID selected by the user
    sublocation_data = data[data['LocationID'] == location_id]

    # create a list of available appointment durations
    durations = ['15 minutes', '30 minutes', '45 minutes', '1 hour', '1.25 hours', '1.5 hours', '1.75 hours', 
                 '2 hours', '2.25 hours', '2.5 hours', '2.75 hours', '3 hours', '3.25 hours', '3.5 hours', '3.75 hours', '4 hours']

    # create a dropdown menu that allows the user to select the duration of the appointment
    duration = st.selectbox('Select the duration of the appointment', durations)

    # divide everything into 30 minute increments to later determine if the appointment can be scheduled
    # create a dictionary that converts the values in the durations list to the number of 30 minute blocks required
    appointment_blocks = {'15 minutes':1, '30 minutes':2, '45 minutes':3, '1 hour':4, '1.25 hours':5, '1.5 hours':6, '1.75 hours':7, '2 hours':8, 
                          '2.25 hours':9, '2.5 hours':10, '2.75 hours':11, '3 hours':12, '3.25 hours':13, '3.5 hours':14, '3.75 hours':15, '4 hours':16}

    # create a list that contains the waiting period until the next appointment can be scheduled
    waiting_periods = {'Tomorrow':1,'1 week':7, '1 month':30, '3 months':90, '6 months':180, '1 year':365}

    # create a dropdown menu that allows the user to select the appointment interval
    waiting_period = st.selectbox('Select followup window', waiting_periods)
    waiting_days = waiting_periods[waiting_period]
    first_date_allowed = (pd.to_datetime('today') + pd.DateOffset(days = waiting_days)).date()

    # determine how many appointments are currently schedule for the selected location in the sublocation_data dataframe starting on the first_date_allowed variable
    appointments = sublocation_data[sublocation_data['Date'] >= first_date_allowed]

    # add a column to the dataframe that contains the count of observations for each Date and keep the last observation for each Date
    daily_location_appointments = appointments.groupby('Date', as_index = False)['AppointmentID'].count()
    daily_location_appointments['Date'] = pd.to_datetime(daily_location_appointments['Date'])

    # create a column that says which day of the week each date is
    daily_location_appointments['DoW'] = daily_location_appointments['Date'].dt.day_name() 

    # create a list of the days of the week
    #days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # create a multisection dropdown menu that allows the user to select the days of the week they want to schedule the appointment 
    #dow = st.multiselect('Select the days of the week you want to schedule the appointment', days_of_week)

    # filter the daily_location_appointments dataframe to only include the days of the week selected by the user
    #daily_location_appointments = daily_location_appointments[daily_location_appointments['DoW'].isin(dow)]

    # create a new column that is the string value of the Date column
    daily_location_appointments['sDate'] = daily_location_appointments['Date'].astype(str)

    # create a calendar that begins starts the waiting_period number of months from today by selecting the corresponding value from the key in the waiting_periods dictionary
    appointment = st.subheader(f'Based on a {waiting_period} appointment frequency, do not schedule anything before {first_date_allowed}.')

    # create an empty dataframe that contains a column with observations for each 15 minute window from 8am to 5pm. format the column as a datetime variable
    time_blocks = pd.DataFrame(pd.date_range(start = '11:00', end = '20:00', freq = '15min').strftime('%H:%M'))
    time_blocks.columns = ['Time']

    # create a new dataframe that contains all of the dates located in the sublocation_data dataframe
    dates = pd.DataFrame(sublocation_data['Date'].unique())
    dates.columns = ['Date']

    # create a new dataframe that contains all of the unique chair id values from the sublocation_data dataframe
    unique_chairs = pd.DataFrame(sublocation_data['Chair ID'].unique())
    unique_chairs.columns = ['Chair ID']
    unique_chairs.sort_values(by = ['Chair ID'], inplace = True)

    # create a new dataframe that contains all of the unique combinations of chair id from the unique_chairs dataframe and date from the dates dataframe
    chairs = unique_chairs.assign(key=1).merge(dates.assign(key=1), on='key').drop('key', 1)
    chairs.sort_values(by = ['Date', 'Chair ID'], inplace = True)
    chairs.reset_index(drop = True, inplace = True)

    # combine the time_blocks and chairs dataframes into a single dataframe that contains all of the possible combinations of chairs and times
    time_blocks = time_blocks.assign(key=1).merge(chairs.assign(key=1), on='key').drop('key', 1)
    time_blocks.sort_values(by = ['Date', 'Time', 'Chair ID'], inplace = True)
    time_blocks.reset_index(drop = True, inplace = True)

    # convert the start time column from the sublocation_data dataframe to a datetime variable
    sublocation_data['Start Time'] = pd.to_datetime(sublocation_data['Start Time'])
    sublocation_data['End Time'] = pd.to_datetime(sublocation_data['End Time'])

    # create a new column in the sub_location_data dataframe that contains the time part of the start time variable
    sublocation_data['StartHour'] = sublocation_data['Start Time'].dt.strftime('%H:%M')
    sublocation_data['EndHour'] = sublocation_data['End Time'].dt.strftime('%H:%M')

    # merge sublocation with time_blocks so that the sublocation dataframe merges to all times and chair ids in the time_blocks dataframe where the time in the time_blocks dataframe is >= the start time in the sublocation dataframe and <= the end time in the sublocation dataframe
    sublocation_data = time_blocks.merge(sublocation_data, how = 'left', left_on = ['Date', 'Time', 'Chair ID'], right_on = ['Date', 'StartHour', 'Chair ID'])
    
    # forward fill all columns in the sublocation_data dataframe until EndHour is >= time and grouped by Date and Chair ID.
    columns = sublocation_data.columns.tolist()
    columns = [x for x in columns if x not in ['Time', 'Chair ID', 'Date']]
    sublocation_data[columns] = sublocation_data.groupby(['Date', 'Chair ID'])[columns].ffill()

    # set the column values to missing if the endhour is <= time
    sublocation_data.loc[sublocation_data['EndHour'] <= sublocation_data['Time'], columns] = np.nan    

    # using appointment_blocks, create a variable that tells us how many 30 minute blocks are required for the appointment
    appointment_blocks_required = appointment_blocks[duration]

    # create a measure that counts the consecutive number of missing observations in the sublocation_data dataframe grouped by Date and Chair ID and restart the count when a non-missing observation is encountered
    sublocation_data.sort_values(by = ['Date', 'Chair ID', 'Time'], inplace = True)
    sublocation_data.reset_index(drop = True, inplace = True)
    sublocation_data['Missing'] = sublocation_data.groupby(['Date', 'Chair ID'])['AppointmentID'].apply(lambda x: x.isnull().cumsum())

    # create a new variable that contains the value of missing only when appointmentid is non missing
    sublocation_data['TempMissing'] = np.where(sublocation_data['AppointmentID'].isnull(), np.nan, sublocation_data['Missing'])

    # forward fill the tempmissing variable
    sublocation_data['TempMissing'] = sublocation_data.groupby(['Date', 'Chair ID'])['TempMissing'].ffill()

    # fill tempmissing null values with 0
    sublocation_data['TempMissing'].fillna(0, inplace = True)
    
    # create a new variable called consecutive_avails_temp as the difference between missing and tempmissing
    sublocation_data['ConsecutiveAvails_temp'] = sublocation_data['Missing'] - sublocation_data['TempMissing']

    # trying grouping by date, chair, and TempMissing and then using the max function to get the max consecutive avails
    sublocation_data['ConsecutiveAvails_max'] = sublocation_data.groupby(['Date', 'Chair ID', 'TempMissing'])['ConsecutiveAvails_temp'].transform('max')

    # add one to the consecutive avails max variable
    sublocation_data['ConsecutiveAvails'] = sublocation_data['ConsecutiveAvails_max'] + 1

    # create a new variable that is the difference between consecutive avails and consecutive avails temp
    sublocation_data['AvailableWindow'] = sublocation_data['ConsecutiveAvails'] - sublocation_data['ConsecutiveAvails_temp']

    # if appointmentid is not null, set available window to 0
    sublocation_data.loc[sublocation_data['AppointmentID'].notnull(), 'AvailableWindow'] = 0

    # drop columns missing, tempmissing, consecutiveavails_temp, consecutiveavails_max, consecutiveavails
    sublocation_data.drop(columns = ['Missing', 'TempMissing', 'ConsecutiveAvails_temp', 'ConsecutiveAvails_max', 'ConsecutiveAvails'], inplace = True)

    # fill in all null locationid and locationname values with a forward fill and then a backfill
    sublocation_data['LocationID'].fillna(method = 'ffill', inplace = True)
    sublocation_data['LocationName'].fillna(method = 'ffill', inplace = True)
    sublocation_data['LocationID'].fillna(method = 'bfill', inplace = True)
    sublocation_data['LocationName'].fillna(method = 'bfill', inplace = True)

    # create a new dataframe that contains only open appointments by dropping all observations where appointmentid is not null
    open_appointments = sublocation_data[sublocation_data['AppointmentID'].isnull()]

    # filter open_appointments to only include observations where availablewindow is >= appointment_blocks_required
    open_appointments = open_appointments[open_appointments['AvailableWindow'] >= appointment_blocks_required]

    # Determine how many chairs are at the selected location
    location_data = data[data['LocationID'] == location_id]
    location_chairs = location_data['Chairs'].iloc[0]

    # 3 observation days * 3 time slots per day * number of chairs at the location
    ob_days = 3
    obs_per_day = 3
    chair_display = ob_days * obs_per_day * location_chairs

    # create a new dataframe from open_appointments where first_date_allowed >= date and retain the first 3 unique date values
    open_appointments = open_appointments[open_appointments['Date'] >= first_date_allowed].groupby('Date').head(obs_per_day)
    open_appointments = open_appointments.head(chair_display)
    
    # create a statement that will print each unique date in the open_Appointments dataframe and the corresponding time variable
    st.subheader('The following dates and times are available for your appointment:')
    try:
        if len(open_appointments) <= 3:
            st.write(f'The closest available appointment date that is at least **{waiting_period}** from now is **{open_appointments["Date"].iloc[0]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[0]}** in chair **{open_appointments["Chair ID"].iloc[0]}**, \
                     **{open_appointments["Time"].iloc[1]}** in chair **{open_appointments["Chair ID"].iloc[1]}**, \
                     **{open_appointments["Time"].iloc[2]}** in chair **{open_appointments["Chair ID"].iloc[2]}**.')
        elif len(open_appointments) <= 6:
            st.write(f'The closest available appointment date that is at least **{waiting_period}** from now is **{open_appointments["Date"].iloc[0]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[0]}** in chair **{open_appointments["Chair ID"].iloc[0]}**, \
                     **{open_appointments["Time"].iloc[1]}** in chair **{open_appointments["Chair ID"].iloc[1]}**, \
                     **{open_appointments["Time"].iloc[2]}** in chair **{open_appointments["Chair ID"].iloc[2]}**.')
            st.markdown("""---""")
            st.write(f'The second closest available appointment date from now is **{open_appointments["Date"].iloc[3]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[3]}** in chair **{open_appointments["Chair ID"].iloc[3]}**, \
                     **{open_appointments["Time"].iloc[4]}** in chair **{open_appointments["Chair ID"].iloc[4]}**, \
                     **{open_appointments["Time"].iloc[5]}** in chair **{open_appointments["Chair ID"].iloc[5]}**.')
        else:
            st.write(f'The closest available appointment date that is at least **{waiting_period}** from now is **{open_appointments["Date"].iloc[0]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[0]}** in chair **{open_appointments["Chair ID"].iloc[0]}**, \
                     **{open_appointments["Time"].iloc[1]}** in chair **{open_appointments["Chair ID"].iloc[1]}**, \
                     **{open_appointments["Time"].iloc[2]}** in chair **{open_appointments["Chair ID"].iloc[2]}**.')
            st.markdown("""---""")
            st.write(f'The second closest available appointment date from now is **{open_appointments["Date"].iloc[3]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[3]}** in chair **{open_appointments["Chair ID"].iloc[3]}**, \
                     **{open_appointments["Time"].iloc[4]}** in chair **{open_appointments["Chair ID"].iloc[4]}**, \
                     **{open_appointments["Time"].iloc[5]}** in chair **{open_appointments["Chair ID"].iloc[5]}**.')
            st.markdown("""---""")
            st.write(f'The third closest available appointment date from now is **{open_appointments["Date"].iloc[6]}**.')
            st.write(f'Please select a time from the following list of available times: **{open_appointments["Time"].iloc[6]}** in chair **{open_appointments["Chair ID"].iloc[6]}**, \
                     **{open_appointments["Time"].iloc[7]}** in chair **{open_appointments["Chair ID"].iloc[7]}**, \
                     **{open_appointments["Time"].iloc[8]}** in chair **{open_appointments["Chair ID"].iloc[8]}**.')
    except:
        st.write(f'You need to return after **{waiting_period}** and any date is available on or after **{first_date_allowed}**.')

    # create a new dataframe that contains all dates, not just those within the daily_location_appointments dataframe. Ending date should be 2 years from today.
    st.markdown("""---""")
    st.write('Please look at the below dates as possible options only if the above dates do not work. These dates currently have zero appointments.')
    start_date = first_date_allowed
    end_date = first_date_allowed + datetime.timedelta(days = waiting_days + 14)
    all_dates = pd.DataFrame(pd.date_range(start_date, end_date), columns = ['Date'])
    filtered_dates = all_dates[~all_dates['Date'].isin(daily_location_appointments['Date'])]
    filtered_dates['Day of Week'] = filtered_dates['Date'].dt.day_name()
    filtered_dates['Date'] = filtered_dates['Date'].dt.date 
    st.write(filtered_dates[['Date', 'Day of Week']])

    # create a button that allows the user to submit the selected location and appointment
    #submit = st.button('Submit')

    # create a conditional statement that will only run if the user clicks the submit button
    # if submit:

    #     st.write(f'The appointment has been scheduled at the **{location}** on **{appointment}** for **{duration}**. \
    #     The patient\'s name is **{patient_name}**, their date of birth is **{patient_dob}**, and their phone number is **{patient_phone}**. \
    #     Please confirm the appointment information is correct and click the button below to confirm the appointment.')

    #     # create a button that allows the user to confirm the appointment
    #     confirm = st.button('Confirm Appointment')

    # create a button that completely reloads the streamlit page
    if st.button('Restart Scheduler or Schedule a New Appointment'):
        st.session_state.schedule_appointment = False
        st.experimental_rerun()
 


