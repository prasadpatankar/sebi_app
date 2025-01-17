import streamlit as st
import pandas as pd
import os
import openpyxl
import base64
import numpy as np

# Correct file path
file_path = r"files/database_home.xlsx"
stock_var_list = ['YTD', 'AUM', 'MCAP', "No_scheme", "No_Folios", "Market_Cap", "_Index"]

# Load the Excel file (use openpyxl engine if encountering errors)
try:
    db_home = pd.read_excel(file_path, engine="openpyxl")
except FileNotFoundError:
    st.error(f"Database file ({file_path}) not found. Please check the path.")
    st.stop()  # Stop execution if the file is not found
except Exception as e:
    st.error(f"An error occurred loading the database file: {e}")
    st.stop()

st.title("Filter Database Tables")

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
        data = df.replace(np.nan,"")

        categorical_cols = []
        for col in data.columns:
            # Convert to string and replace NaN with empty string for accurate counting
            cleaned_column = data[col].astype(str).str.strip().str.replace("nan",'')
            if cleaned_column.str.contains(r'[a-zA-Z]', regex=True).sum() > 5:
                categorical_cols.append(col)

        unique_values = {}
        for col in categorical_cols:
            unique_values[col] = list(data[col].unique())

        # Create filter text boxes with auto-prompt
        num_cols = 3
        cols = st.columns(num_cols)  # Create 3 columns

        # Counter for iterating through columns
        col_index = 0

        filters = {}
        for column, unique_vals in unique_values.items():
            with cols[col_index % num_cols]:  # Use modulo to cycle through columns
                selected_values = st.multiselect(
                    f"Filter {column}:",
                    unique_vals,
                    key=f"multiselect_{column}"
                )
                filters[column] = selected_values
            col_index += 1  # Increment column index
        #"""Filters the DataFrame based on the provided filter dictionary."""
        filtered_df = data.copy()
        for column, values in filters.items():
            if values:  # Check if there are any filter values for this column
                filtered_df = filtered_df[filtered_df[column].isin(values)]

        # Display the filtered DataFrame
        st.write("Filtered DataFrame:")
        st.dataframe(filtered_df)


    except:
        "error in loading file"





