import streamlit as st
from streamlit_option_menu import option_menu
import os
import google.generativeai as genai

# Define page titles and corresponding file paths
page_titles = {
"Dashboard": "mydashboard.py",
"Database": "database.py",
"Filter Data": "filterdf.py",
"Utilities": "pagetwo.py",
}

# Function to load and display a page based on the selected title
def load_page(page_title):
    if page_title in page_titles:
        file_path = os.path.join("pages", page_titles[page_title])
        st.page_link(page=file_path, label=page_title, icon="🏠")
        
        if os.path.exists(file_path):
            try:
                exec(open(file_path, encoding='utf-8').read())
            except UnicodeDecodeError as e:
                st.error(f"Error loading page '{page_title}': {str(e)}")
        else:
            st.error(f"Page '{page_title}' not found.")
    else:
        st.error("Invalid page title.")

# Create the main app
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Welcome to SEBI Dashboards & Database",
        page_icon="📈",
        layout= "wide",
        initial_sidebar_state="collapsed"
    )

    # Display the top-level title
    st.title("Database of Indian Securities Market (DISM)")

    # Create the navigation bar using option_menu
    selected_page = option_menu(
        menu_title="",
        options=list(page_titles.keys()),
        icons=["speedometer2", "database", "wrench", "robot", "cart-plus"],

        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "5px"},
            "icon": {"color": "blue", "font-size": "25px"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "onmouseover": """
                    function(e) {
                        const link = e.target.closest('a');
                        if (link) {
                            const pageTitle = link.textContent; // Get the page title
                            const pagePath = link.getAttribute('href'); // Get existing href
                            link.setAttribute('href', 'https://sebiapp.streamlit.app/?page=' + pageTitle); // Modify href with your Streamlit Cloud URL
                        }
                    }
                """,
                "onmouseout": """
                    function(e) {
                        const link = e.target.closest('a');
                        if (link) {
                            link.setAttribute('href', 'https://sebiapp.streamlit.app/'); // Restore href to your Streamlit Cloud URL
                        }
                    }
                """,
            }
        }
        
    )

    # Load and display the selected page
    load_page(selected_page)

if __name__ == "__main__":
    main()
