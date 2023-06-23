"""
author: f.romadhana@gmail.com
Grab E-Receipt Dashboard: Analyzing Grab Bike and Grab Food Transactions

"""

#import necessary libraries
import re
import pytz
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from imaplib import IMAP4_SSL
from bs4 import BeautifulSoup
from email import message_from_bytes

# Function to convert the date to UTC+7 timezone
def convert_to_utc7(date_string):
    # Parse the date string using the email format
    date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

    # Get the UTC timezone
    utc_timezone = pytz.timezone('UTC')

    # Convert the date to UTC timezone
    date_utc = date.astimezone(utc_timezone)

    # Get the UTC+7 timezone
    utc7_timezone = pytz.timezone('Asia/Jakarta')

    # Convert the date to UTC+7 timezone
    date_utc7 = date_utc.astimezone(utc7_timezone)

    # Format the date as a string
    date_formatted = date_utc7.strftime("%Y-%m-%d %H:%M:%S")

    return date_formatted

# Function to extract the first HTML table from an email body for Grab Bike
def get_table_grab_bike(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    # Find the "Total Paid" element
    table_element = soup.find('td', string='Total Paid')
    if table_element:
        # Extract the value from the next sibling element
        value_element = table_element.find_next_sibling('td')
        table_value = value_element.text.strip()

        # Remove non-digit characters and 'RP'
        table_value = re.sub(r'[^0-9]', '', table_value)

        if table_value:
            return int(table_value)

    return None

# Function to extract the entire HTML email body for Grab Bike
def get_body_grab_bike(message):
    body_parts = []

    for part in message.walk():
        content_type = part.get_content_type()

        if 'text' in content_type:
            body_parts.append(part.get_payload(decode=True).decode('utf-8'))
        elif 'multipart' in content_type:
            for subpart in part.get_payload():
                subpart_content_type = subpart.get_content_type()
                if 'text' in subpart_content_type:
                    body_parts.append(subpart.get_payload(decode=True).decode('utf-8'))

    return '\n'.join(body_parts)

# Function to extract the first HTML table from an email body for Grab Food
def get_table_grab_food(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    total_value = None
    #find all <td> elements in the HTML
    td_elements = soup.find_all('td')
    for td_element in td_elements:
        #check if the text of the <td> element matches the pattern "TOTAL (INCL. TAX)"
        if re.search(r'TOTAL \(INCL\. TAX\)', td_element.text):
            #get the next sibling element
            next_element = td_element.find_next_sibling()
            if next_element is not None:
                #extract the value using a regular expression
                match = re.search(r'(\d+)', next_element.text)
                if match:
                    total_value = int(match.group(1))
                    break

    return total_value

# Function to extract the entire HTML email body for Grab Food
def get_body_grab_food(message):
    body_parts = []
    for part in message.walk():
        content_type = part.get_content_type()
        if 'text' in content_type:
            body_parts.append(part.get_payload(decode=True).decode('utf-8'))
        elif 'multipart' in content_type:
            for subpart in part.get_payload():
                subpart_content_type = subpart.get_content_type()
                if 'text' in subpart_content_type:
                    body_parts.append(subpart.get_payload(decode=True).decode('utf-8'))
    return '\n'.join(body_parts)


# Connect gmail account
with IMAP4_SSL('imap.gmail.com') as mail:
    mail.login(st.secrets["gmail_account"]["gmail"], st.secrets["gmail_account"]["pass"])
    mail.select('Inbox')

    # Fetch Grab Bike e-receipts
    _, grab_bike_message_numbers = mail.search(None, 'SUBJECT "[Jasamarga] Your Grab E-Receipt"')

    emails_grab_bike = []
    for num in grab_bike_message_numbers[0].split():
        _, message_data = mail.fetch(num, '(RFC822)')
        message = message_from_bytes(message_data[0][1])

        body_html_grab_bike = get_body_grab_bike(message)
        table_value_grab_bike = get_table_grab_bike(body_html_grab_bike)

        date_utc7 = convert_to_utc7(message['Date'])

        emails_grab_bike.append({
            'date': date_utc7,
            'grab_bike': table_value_grab_bike
        })

    # Convert Grab Bike emails to a DataFrame
    grab_bike_df = pd.DataFrame(emails_grab_bike)

    # Convert 'date' column to datetime.date type
    grab_bike_df['date'] = pd.to_datetime(grab_bike_df['date']).dt.date


    # Fetch Grab Food e-receipts
    _, grab_food_message_numbers = mail.search(None, 'NOT SUBJECT "[Jasamarga] Your Grab E-Receipt" SUBJECT "Your Grab E-Receipt"')

    emails_grab_food = []
    for num in grab_food_message_numbers[0].split():
        _, message_data = mail.fetch(num, '(RFC822)')
        message = message_from_bytes(message_data[0][1])

        body_html_grab_food = get_body_grab_food(message)
        table_value_grab_food = get_table_grab_food(body_html_grab_food)

        date_utc7 = convert_to_utc7(message['Date'])

        emails_grab_food.append({
            'date': date_utc7,
            'grab_food': table_value_grab_food
        })

    # Convert Grab Food emails to a DataFrame
    grab_food_df = pd.DataFrame(emails_grab_food)

    # Convert 'date' column to datetime.date type
    grab_food_df['date'] = pd.to_datetime(grab_food_df['date']).dt.date

    # Merge Grab Bike and Grab Food DataFrames
    merged_df = pd.merge(grab_bike_df, grab_food_df, on='date', how='outer')

    # Fill missing values with zeros
    merged_df = merged_df.fillna(0)

    # Group by 'date' and calculate the sum of 'grab_bike' per day
    grab_bike_sum = merged_df.groupby('date')['grab_bike'].sum().reset_index()

    # Merge the 'grab_bike' sum with the original 'grab_food' DataFrame
    merged_df = pd.merge(grab_bike_sum, grab_food_df, on='date', how='left')

    # Fill missing values with zeros
    merged_df['grab_food'] = merged_df['grab_food'].fillna(0).astype(int)

    # Calculate the total column
    merged_df['total'] = merged_df['grab_bike'] + merged_df['grab_food']

    # Filter DataFrame by date range
    st.subheader("Grab E-Receipt Dashboard 🛺")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    # Apply date filter
    mask = (merged_df['date'] >= start_date) & (merged_df['date'] <= end_date)
    filtered_df = merged_df.loc[mask].copy()

    # Add a number column to the DataFrame
    filtered_df.loc[:, 'no.'] = range(1, len(filtered_df) + 1)

    # Rearrange the columns in the DataFrame
    filtered_df = filtered_df[['no.', 'date', 'grab_bike', 'grab_food', 'total']]

    # Convert the DataFrame to HTML without the index column
    table_html = filtered_df.to_html(index=False)

    # Display the table in Streamlit using st.markdown
    st.write("Transactions Table")
    st.markdown(table_html, unsafe_allow_html=True)

    # Calculate the sum and average of grab_bike values
    grab_bike_total_sum = filtered_df['grab_bike'].sum()
    formatted_grab_bike_total_sum = "Rp {:,.0f}".format(grab_bike_total_sum)

    grab_bike_average = filtered_df['grab_bike'].mean()
    formatted_grab_bike_average = "Rp {:,.0f}".format(grab_bike_average)

    # Calculate the sum and average of grab_food values
    grab_food_total_sum = filtered_df['grab_food'].sum()
    formatted_grab_food_total_sum = "Rp {:,.0f}".format(grab_food_total_sum)

    grab_food_average = filtered_df.loc[filtered_df['grab_food'] > 0, 'grab_food'].mean()
    formatted_grab_food_average = "Rp {:,.0f}".format(grab_food_average)

    # Calculate the total (grab_bike + grab_food) and the average of total
    total_sum = filtered_df['total'].sum()
    formatted_total_sum = "Rp {:,.0f}".format(total_sum)

    total_average = filtered_df['total'].mean()
    formatted_total_average = "Rp {:,.0f}".format(total_average)

    st.title(" ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Grab Bike Total", formatted_grab_bike_total_sum)
        st.metric("Grab Bike Average", formatted_grab_bike_average)
    with col2:
        st.metric("Grab Food Total", formatted_grab_food_total_sum)
        st.metric("Grab Food Average", formatted_grab_food_average)
    with col3:
        st.metric("Total (GB+GF)", formatted_total_sum)
        st.metric("Average Total", formatted_total_average)

    # Create a line chart from the filtered DataFrame
    chart_data = filtered_df[['date', 'grab_bike', 'grab_food']].copy()

    # Convert 'date' column to datetime
    chart_data['date'] = pd.to_datetime(chart_data['date'])

    # Melt the DataFrame to reshape it for plotting
    chart_data_melted = chart_data.melt('date', var_name='category', value_name='value')

    # Configure the plot
    fig = px.line(chart_data_melted, x='date', y='value', color='category')

    # Set the x-axis tick format as dates
    fig.update_layout(xaxis_tickformat='%a, %b-%d')

    # Add a title to the chart
    fig.update_layout(title='Transactions Line Chart')

    # Display the plot in Streamlit
    st.plotly_chart(fig)