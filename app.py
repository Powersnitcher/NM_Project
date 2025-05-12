# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import secrets
from twilio.rest import Client

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("accident.csv")

df = load_data()
st.title("🚦 AI-Driven Road Accident Analysis & Alert System")

# ----------------------------- #
# Analysis Section
# ----------------------------- #

st.header("1. Reasons for Road Accidents")
reason_counts = df['Reason'].value_counts()
colors = plt.cm.Spectral(np.linspace(0, 1, len(reason_counts)))
fig1, ax1 = plt.subplots()
ax1.pie(reason_counts, labels=reason_counts.index, colors=colors, autopct='%1.1f%%', startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

st.header("2. Top 10 States by Number of Accidents")
state_accidents = df.groupby('State')['Accident_ID'].count().reset_index()
top_states = state_accidents.sort_values(by='Accident_ID', ascending=False).head(10)
colors = plt.cm.Spectral(top_states['Accident_ID'] / float(max(top_states['Accident_ID'])))
fig2, ax2 = plt.subplots()
ax2.barh(top_states['State'], top_states['Accident_ID'], color=colors)
ax2.set_xlabel("Number of Accidents")
st.pyplot(fig2)

st.header("3. Accidents by Weather Condition")
weather_stats = df.groupby('Weather_Conditions')['Accident_ID'].count().reset_index()
top_weather = weather_stats.sort_values(by='Accident_ID', ascending=False).head(10)
colors = plt.cm.Spectral_r(top_weather['Accident_ID'] / float(max(top_weather['Accident_ID'])))
fig3, ax3 = plt.subplots()
ax3.bar(top_weather['Weather_Conditions'], top_weather['Accident_ID'], color=colors)
ax3.set_xticklabels(top_weather['Weather_Conditions'], rotation=45)
st.pyplot(fig3)

st.header("4. Impact of Speeding on Fatalities")
speed_stats = df.groupby('Speed_Limit', as_index=False)['Number_of_Deaths'].mean()
fig4, ax4 = plt.subplots()
ax4.plot(speed_stats['Speed_Limit'], speed_stats['Number_of_Deaths'], label='Avg Deaths')
ax4.set_xlabel("Speed Limit")
ax4.set_ylabel("Average Deaths")
ax4.legend()
st.pyplot(fig4)

st.header("5. Alcohol-Related Accidents by State")
alcohol_df = df[df['Alcohol_Involved'] == 'Yes']
state_counts = alcohol_df['State'].value_counts()
fig5, ax5 = plt.subplots()
ax5.bar(state_counts.index, state_counts.values, color=plt.cm.Spectral(state_counts.values/max(state_counts.values)))
ax5.set_xticklabels(state_counts.index, rotation=90, fontsize=8)
st.pyplot(fig5)

st.header("6. Urban vs Rural Accident Distribution")
df['Location_Type'] = df['Road_Type'].apply(lambda x: 'Rural' if str(x).startswith('R') else 'Urban')
location_counts = df['Location_Type'].value_counts()
fig6, ax6 = plt.subplots()
ax6.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%', colors=['#ff7f0e', '#1f77b4'])
st.pyplot(fig6)

# ----------------------------- #
# Alert System Section
# ----------------------------- #
st.header("🚨 Real-Time Driver Alert System")

alcohol_input = st.radio("Have you consumed alcohol?", ["Yes", "No"])
alcohol_detected = (alcohol_input == "Yes")

# Captcha check if alcohol is "No"
if not alcohol_detected:
    captcha_key = secrets.token_hex(3)
    st.markdown(f"Captcha: **{captcha_key}**")
    user_answer = st.text_input("Enter the captcha above")
    if st.button("Verify Captcha"):
        if user_answer == captcha_key:
            st.success("Captcha matched. Proceed.")
        else:
            st.error("Captcha failed. Assuming alcohol detected.")
            alcohol_detected = True

# Speed Input
speed = st.number_input("Enter your current speed (km/h):", min_value=0)

# SMS Alert
if st.button("Trigger Alert"):
    try:
        # Load Twilio secrets
        account_sid = st.secrets["TWILIO_SID"]
        auth_token = st.secrets["TWILIO_TOKEN"]
        from_number = st.secrets["TWILIO_FROM"]
        to_number = st.secrets["TWILIO_TO"]
        client = Client(account_sid, auth_token)

        messages_sent = []

        if speed > 100:
            body = f"🚗 Overspeeding detected: {speed} km/h"
            client.messages.create(body=body, from_=from_number, to=to_number)
            messages_sent.append(body)

        if alcohol_detected:
            body = "🍺 Alcohol detected! Driver attempting to drive."
            client.messages.create(body=body, from_=from_number, to=to_number)
            messages_sent.append(body)

        if messages_sent:
            st.success("Alerts sent:\n" + "\n".join(messages_sent))
        else:
            st.success("✅ You are driving safely.")

    except Exception as e:
        st.error(f"Error sending SMS: {e}")
