import streamlit as st
from streamlit_option_menu import option_menu
import os


# Define page titles and corresponding file paths
page_titles = {
    "Dashboard": "pageone.py",
    "Merge PDFs": "pagetwo.py",
    "Database": "dashboard.py",
    "ChatGPT": "ChatGPT.py",
  }


# Function to load and display a page based on the selected title
def load_page(page_title):
    if page_title in page_titles:
        file_path = os.path.join("pages", page_titles[page_title])
        if os.path.exists(file_path):
            exec(open(file_path).read())
        else:
            st.error(f"Page '{page_title}' not found.")
    else:
        st.error("Invalid page title.")

# Create the main app
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Welcome to SEBI Dashboards & Database",
        page_icon="💬",
        layout= "wide",
        initial_sidebar_state="collapsed"
    )

    # Display the top-level title
    st.title("DEPA DASHBOARD")

    # Create the navigation bar using option_menu
    selected_page = option_menu(
        menu_title="",
        options=list(page_titles.keys()),
        icons=["home", "info-circle", "envelope", "cart-plus"],
        default_index=1,
        orientation="horizontal",
        styles={
            "container": {"padding": "5px"},
            "icon": {"color": "blue", "font-size": "25px"},
            "nav-link": {"font-size": "18px", "text-align": "left"},
        }
        
    )

    # Load and display the selected page
    load_page(selected_page)

if __name__ == "__main__":
    main()