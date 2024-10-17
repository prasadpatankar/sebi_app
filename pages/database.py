import streamlit as st
import pandas as pd
import os
import openpyxl
import base64
import numpy as np

# --- Function Definitions --- 
def has_alphabet(dfx):
    alphabet_columns = []
    for col in dfx.columns:
        cleaned_column = dfx[col].astype(str).str.strip().str.replace("nan",'')
        if cleaned_column.str.contains(r'[a-zA-Z]', regex=True).sum() > 5:
            alphabet_columns.append(col)
    return alphabet_columns

def display_data(df, selected_table):
    st.markdown(f"<center><h3>{selected_table}</h3></center>", unsafe_allow_html=True)
    st.markdown('<div style="overflow-x:auto;">', unsafe_allow_html=True)
    styled_table = df.iloc[-11:].style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td:nth-child(n+2)', 'props': [('text-align', 'right')]}
    ]).to_html()
    st.write(styled_table, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) 

"""def check_partial_match(column_name, list_b):
    for item in list_b:
        if item in column_name:
            return True
    return False"""

def check_partial_match(column_name, list_b):
    """Checks if any element in list_b is present as a substring in column_name."""
    return any(item.lower() in column_name.lower() for item in list_b)

def match_cols(dfa, list_b):
    """Match columns in the dataframe that partially match items in list_b."""
    return [column for column in dfa.columns if check_partial_match(column, list_b)]

def to_financial_year(date):
  if date.month <= 3:  # January to March falls in the previous FY
    financial_year = f"{date.year - 1}-{str(date.year)[2:]}"
  else:  # April to December falls in the current FY
    financial_year = f"{date.year}-{str(date.year + 1)[2:]}"

  return financial_year


st.title("Database Table Viewer")

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
    table_a = table_id.replace("_m_", "_a_")
    filename_a = f"{table_a}.csv"
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
        
        # Create radio buttons using st.radio
        frequency = st.radio("Select Data Frequency:", ["Monthly", "Annual"])
        
        if frequency == "Monthly":
            #formatted_df = df.apply(format_dataframe)
            #st.write(formatted_df.tail())
            display_data(df,selected_table)
            
            # --- Download button ---
            csv = df.to_csv(index=False) # Convert DataFrame to CSV string
            b64 = base64.b64encode(csv.encode()).decode()  # Encode as base64
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Monthly CSV Data</a>'
            st.markdown(href, unsafe_allow_html=True)


        else:
            try:
                #convert dataframe to annual
                annual_df = pd.DataFrame()
                if "Listing_Date" in df.columns:
                    df['Month'] = pd.to_datetime(df['Listing_Date'], format='mixed')
                if "Month" in df.columns:
                    group_col = []
                    for col in df.columns:
                        # Convert to string and replace NaN with empty string for accurate counting
                        cleaned_column = df[col].astype(str).str.strip().str.replace("nan",'')
                        if cleaned_column.str.contains(r'[a-zA-Z]', regex=True).sum() > 5:
                            group_col.append(col)
                    numeric_col = list(set(df.columns) - set(group_col) - set(["Month"])) 
                    # Replace commas in all columns
                    df[numeric_col] = df[numeric_col].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
                    # Convert the 'Month' column to datetime objects
                    df['Month'] = pd.to_datetime(df['Month'], format='mixed')
                    
                    # Create radio buttons using st.radio
                    frequency1 = st.radio("Select Year Type:", ["Financial Year", "Calender Year"])
                    if frequency1 == "Financial Year":
                        df['Year'] = df['Month'].apply(to_financial_year)            
                    else:
                        df['Year'] = df['Month'].dt.year           

                    new_factlist = ['Year'] + group_col
                    try:                    
                        df = df.drop('Month', axis=1)
                    except:
                        pass

                    match_col = []
                    for column in df.columns:
                        for item in stock_var_list:
                            if item.lower() in column.lower():
                                match_col.append(column)
                                break  # Move to the next column after finding a match
                    rem_cols = list(set(numeric_col) - set(match_col) )
                    agg_dict = {}
                    for col in match_col:
                        agg_dict[col] = 'last'
                    for col in rem_cols:
                        agg_dict[col] = 'sum'
                    annual_df = df.groupby(new_factlist).agg(agg_dict).reset_index()                   
                    #formatted_df1 = format_dataframe(annual_df)
                    
                    formatted_df = annual_df.copy()
                    for column in formatted_df.columns:
                        if pd.api.types.is_numeric_dtype(formatted_df[column]):
                            # Format numeric values (both float and int)
                            formatted_df[column] = formatted_df[column].apply(lambda x: f'{x:,.2f}') 
                        elif pd.api.types.is_datetime64_any_dtype(formatted_df[column]):
                            # Format datetime to date
                            formatted_df[column] = formatted_df[column].dt.strftime('%d-%m-%Y')

                    display_data(formatted_df,selected_table)
                    #download_data(annual_df, f"Annual_{filename}")

                    # --- Download button ---
                    csv = annual_df.to_csv(index=False) # Convert DataFrame to CSV string
                    b64 = base64.b64encode(csv.encode()).decode()  # Encode as base64
                    href = f'<a href="data:file/csv;base64,{b64}" download="{filename_a}">Download Annual CSV Data</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:    
                    st.write('conversion not possible')
                    
            except:
                st.write("Error in conversion")
   
    except FileNotFoundError:
        st.error(f"File {filename} not found.")
    except Exception as e:
        st.error(f"An error occurred reading or displaying {filename}: {e}")
else:
    st.warning("No tables found for the selected category.")