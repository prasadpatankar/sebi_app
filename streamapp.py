import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="TalkToData",
    page_icon="💬",
    layout="wide",
    #initial_sidebar_state="collapsed"
)


st.title('My First Streamlit App')
st.write('Welcome to my Streamlit app!')
user_input = st.text_input('Enter a custom message:', 'Hello, Prasad!')
#Display the customized message using 
st.write('Customized Message:', user_input)