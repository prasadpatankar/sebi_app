import streamlit as st
import pandas as pd
import os
import openpyxl  # Make sure you have openpyxl installed
import base64
import numpy as np

st.title("Database Table Viewer")

# Correct file path
file_path = r"files/database_home.xlsx"


# Load the Excel file (use openpyxl engine if encountering errors)
try:
    db_home = pd.read_excel(file_path, engine="openpyxl")
except FileNotFoundError:
    st.error(f"Database file ({file_path}) not found. Please check the path.")
    st.stop()  # Stop execution if the file is not found
except Exception as e:
    st.error(f"An error occurred loading the database file: {e}")
    st.stop()


# --- Category Dropdown ---
categories = db_home["Category"].unique()
selected_category = st.selectbox("Select Category", categories)

# --- Table Name Dropdown (filtered by category) ---
filtered_tables = db_home[db_home["Category"] == selected_category]
table_names = filtered_tables["Name"].unique()

if table_names.size > 0:  # Check if any tables exist for the selected category
    selected_table = st.selectbox("Select Table Name", table_names)

    # --- Get Table ID ---
    table_id = filtered_tables[filtered_tables["Name"] == selected_table]["Table"].iloc[0]
    filename = f"{table_id}.csv"
    filepath = os.path.join("files", filename)

    # --- Display Table ---
    try:
        df = pd.read_csv(filepath, index_col=0)  # Read the CSV
        df = df.reset_index()
        for x in df.columns:
            if x=="Upload_Date":
                df = df.drop(x, axis=1)
            if x=="rank":
                df = df.drop(x, axis=1)  
        df = df.replace(np.nan,"")
        # --- Download button ---
        csv = df.to_csv(index=False) # Convert DataFrame to CSV string
        b64 = base64.b64encode(csv.encode()).decode()  # Encode as base64
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV Data</a>'
        st.markdown(href, unsafe_allow_html=True)

        # --- Display DataFrame as HTML table with styling ---
        st.markdown(f"<center><h3>{selected_table}</h3></center>", unsafe_allow_html=True) # Centered heading
        st.markdown('<div style="overflow-x:auto;">', unsafe_allow_html=True)  # For horizontal scroll
        styled_table = df.iloc[-11:].style.set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align headers
            {'selector': 'td:nth-child(n+2)', 'props': [('text-align', 'right')]}  # Right align numeric columns
        ]).to_html()
        st.write(styled_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Closing div for scroll


    except FileNotFoundError:
        st.error(f"File {filename} not found.")

    except Exception as e:
        st.error(f"An error occurred reading or displaying {filename}: {e}")

else:
    st.warning("No tables found for the selected category.")