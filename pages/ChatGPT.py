## Chatbot Code
import google.generativeai as genai
import streamlit as st
import os

# Configure Gemini API key
my_api_key = "AIzaSyDE7hhHqhn_0KgVzJxh9nyhmlhjZVSuCOA"
genai.configure(api_key=my_api_key)#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    st.write(m.name)


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

    response = model.generate_content("What is the future of AI in one sentence?")
    st.write(response.text)

    # Generate content based on the prompt and question
    response = model.generate_content(question)

    # Clean up and return the response
    return response.text.strip()

## Streamlit App
#st.set_page_config(page_title="Basic Database Chatbot")
#st.header("Basic Database Chatbot (using Gemini)")

question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# if submit is clicked
if submit:
    response = get_gemini_response(question)
    # Clean the SQL query to remove any unwanted characters
    cleaned_response = response.replace('```', '').strip()  # Remove any code block formatting
    
    st.subheader("The Gemini Response is")
    st.write(cleaned_response)  # Display the SQL result DataFrame