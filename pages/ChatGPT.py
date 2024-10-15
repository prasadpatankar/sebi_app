import os
import pandas as pd
import google.generativeai as genai
import streamlit as st

# Configure Gemini API key
my_api_key = "AIzaSyDE7hhHqhn_0KgVzJxh9nyhmlhjZVSuCOA"
genai.configure(api_key=my_api_key)#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response(question: str) -> str:
    """
    Load Google Gemini model and generate a response to the given question.

    Args:
        question (str): The user's input question.
        prompt (list): A list containing the system prompt.

    Returns:
        str: The generated response from the Gemini model.
    """
    # Initialize the Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generate content based on the prompt and question
    response = model.generate_content(question)

    # Clean up and return the response
    return response.text.strip()

st.title("Ask GPT")

# Example prompt
user_prompt = input("Enter your query: ")

# Get response from Gemini API
response = get_gemini_response(user_prompt)

# Display the response
print("Response from Gemini API:")
print(response)