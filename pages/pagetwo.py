## Merge PDF
import streamlit as st
from PyPDF2 import PdfMerger
import os
from io import BytesIO  # Import BytesIO
import pandas as pd
import numpy as np
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
import datefinder


st.title("PDF Merger")

uploaded_files = st.file_uploader("Choose your PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    merger = PdfMerger()
    filenames = []

    for uploaded_file in uploaded_files:
        try:
            with open(os.path.join("temp", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            filenames.append(uploaded_file.name)
            merger.append(os.path.join("temp", uploaded_file.name))
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
    if filenames:
        st.success(f"Successfully uploaded and merged: {', '.join(filenames)}")

        # Use BytesIO to store the merged PDF in memory
        buffer = BytesIO()
        merger.write(buffer)
        merger.close()

        # Get the bytes from the buffer
        merged_pdf = buffer.getvalue()


        # Clean up temporary files
        for filename in filenames:
            os.remove(os.path.join("temp", filename))

        # Provide download button
        st.download_button(
            label="Download Merged PDF",
            data=merged_pdf,
            file_name="merged_output.pdf",
            mime="application/pdf",
        )


    if not os.path.exists("temp"):
        os.makedirs("temp")

def find_header_row(df, min_alpha_cols =3):
    import pandas as pd
    for i, row in df.iloc.iterrows():
        rowx = pd.Series(row.values)
        rowx = rowx.fillna("")
        alpha_values = rowx.astype(str).str.contains(r'[a-zA-Z]', na=False)
        count = alpha_values.sum()
        if count > min_alpha_cols:
            return i
            break
          

def process_send(dataframe1):
    from sqlalchemy import create_engine
    import pandas as pd
    import numpy as np
    import datefinder
    df2 = pd.DataFrame()
    ### DATA UPLOAD MCR ###
    Table_Name = "MCR"
    new_data_set = 1
    try:
        st.write("Uploading Data...")

        df =  pd.DataFrame(dataframe1)
        st.write("df")
        st.write(df.head())

        header_row_indices = find_header_row (df)
        st.write("header_row_index")
        st.write(header_row_index)
        
        df1 = df.iloc[header_row_index+1:,:]
        df1.columns = df.iloc[header_row_index]
        column_list = list(df1.columns)
        st.write("df1")
        st.write(df1.head())
        text1 = " ".join(column_list)
        matches = datefinder.find_dates(text1)
        match_list = []
        
        for match in matches:
            match_list.append(match)
        date_x1  = pd.to_datetime(np.unique(match_list).max())
                
        #date_x1 = find_dates1(column_list)
        df1 = df1.dropna(subset = column_list[1])
        df1 = df1[~df1.iloc[:,1].str.contains("sub", case=False)]
        Totals = df1[df1.iloc[:,1].str.contains("Total", case=False)]
        df1["Main_Category"] = np.where(df1.iloc[:,1].str.contains("Total", case=False),df1['Scheme Category'],np.NaN)
        df1["Main_Category"] = df1["Main_Category"].bfill()
        df1["Sub_Category"] = np.where(df1.isna().sum(axis=1)>=4,df1['Scheme Category'],np.NaN)
        df1["Sub_Category"] = df1["Sub_Category"].ffill()
        df1 = df1[df1.iloc[:,1].str.len()>=4]
        df2 = df1[df1.isna().sum(axis=1)<=4]
        df2 = df2[~df2.iloc[:,1].str.contains("Total|Domestic", case=False)]
        
        for row in column_list:
            if "segregated" in str(row).lower():  
                new_data_set = 2
        
        if new_data_set ==2:
        
            if len(df2.columns)!=13:
        
                st.write("error in data - No of columns are {} instaed of {} ".format(len(df2.columns), 13))
        
            else:
        
                df2.columns = ['Sr', 'Scheme_Type', 'No_scheme', 'No_Folios', 'Funds_Mobilised_YTD', 'Redemptions_YTD', 'Net_Inflow_YTD', 'Net_AUM', 'Average_AUM', 'No_Folios_segregated', 'AUM_segregated_folio', 'Main_Category', 'Sub_Category']
        
        
        
        elif new_data_set ==1:
        
            if len(df2.columns)!=13:
        
                st.write("error in data - No of columns are {} instaed of {} ".format(len(df2.columns), 11))
        
            else:
        
                df2.columns = ['Sr', 'Scheme_Type', 'No_scheme', 'No_Folios', 'Funds_Mobilised_YTD', 'Redemptions_YTD', 'Net_Inflow_YTD', 'Net_AUM', 'Average_AUM', 'Main_Category', 'Sub_Category']
        
        df2['Month'] = date_x1 + MonthEnd(0)

        
        df2['Upload_Date'] = datetime.now()
    
        st.write("Data Sucessfully Validated, being uploaded on the database")
    
    except:
      
        st.write("Data Validation Failed. Please check the table format")


    st.write("df2")
    st.write(df2.tail())         
    if new_data_set ==1:
    
        Table_Name = "MCR"
    
    if new_data_set ==2:
    
        Table_Name = "MCR2"


    db="defaultdb"
    host="prasadmysql-sebidatabase1.b.aivencloud.com"
    password="AVNS_5gFFh3T1VBzgguK4J2W"
    port="12352"
    user="avnadmin"
    sql_query = 'mysql+pymysql://'+user+':'+password+'@'+host+':'+port+'/'+db
    engine = create_engine(sql_query)

    df2.to_sql(name=Table_Name, con=engine, if_exists='append', index=False)
    st.write(df2.tail())
    #x2 = date_x1.strftime("%b-%Y")
    query =f"SELECT * FROM MCR"
    df11 = pd.read_sql_query(query, engine)
    
    query =f"SELECT * FROM MCR2"
    df12 = pd.read_sql_query(query, engine)
    df13 = pd.concat([df12.iloc[1:],df11])
    st.write("df13")
    st.write(df13.tail())
    
    df13 = df13[df13['Scheme_Type'].str.len()>=4]
    df13 = df13[df13['Month'] > pd.to_datetime("2019/01/01")]
    df13['Month4'] = df13.Month.dt.year.astype('str')+"_"+df13.Month.dt.month.astype('str')
    df13["rank"] = df13.groupby("Month4")["Month"].rank(method="dense", ascending=False)
    df13["rank1"] = df13.groupby("Month")["Upload_Date"].rank(method="dense", ascending=False)  
    df13 = df13[(df13['rank']==1) & (df13['rank1']==1) ]
    df13.sort_values(by = ['Month'], ascending=False, inplace=True)
    Numeric_columns = ['No_scheme', 'No_Folios',  'Funds_Mobilised_YTD',  'Redemptions_YTD',  'Net_Inflow_YTD', 'Net_AUM',  'Average_AUM',  'No_Folios_segregated', 'AUM_segregated_folio']
    df13[Numeric_columns] = df13[Numeric_columns].apply(pd.to_numeric, errors='coerce')
    df13 = df13[['Month', 'Main_Category',  'Sub_Category', 'Scheme_Type', 'No_scheme', 'No_Folios',  'Funds_Mobilised_YTD',  'Redemptions_YTD',  'Net_Inflow_YTD', 'Net_AUM',  'Average_AUM',  'No_Folios_segregated', 'AUM_segregated_folio','Upload_Date']] 
    df13['Main_Category'] = df13['Main_Category'].str.split("-").str[1]
    df13.sort_values(by = ['Month'], inplace=True)
    with open('files/MF_m_01.csv', 'w') as f:
        df13.to_csv(f, index=False)
    st.write(df13.head())
    
    #df13a = format_dataframe(df13)
    
    df13.to_sql(name="MF_m_01", con=engine, if_exists='replace', index=False)
    df14 = df13.groupby(['Month','Main_Category'])[Numeric_columns].sum().reset_index()
    #df14a = format_dataframe(df14) 
    df14.to_sql(name="MF_m_04", con=engine, if_exists='replace', index=False)
    
    df15 = df13.groupby(['Month','Sub_Category'])[Numeric_columns].sum().reset_index()
    #df15a = format_dataframe(df15)
    df15.to_csv(os.path.join('files','MF_m_03.csv'))
    df15.to_sql(name="MF_m_03", con=engine, if_exists='replace', index=False)
    
    df16 = df13.groupby(['Month'])[Numeric_columns].sum().reset_index()
    df16["Net_Inflow"] = np.where(df16["Month"].dt.month == 4, df16["Net_Inflow_YTD"], df16["Net_Inflow_YTD"] -     df16["Net_Inflow_YTD"].shift(1))
    df16 = df16[["Month","No_scheme", "No_Folios",  "Net_Inflow", "Net_Inflow_YTD", "Net_AUM",  "Average_AUM"]]
    df16.to_csv(os.path.join('files','MF_m_02.csv'))
    #df16a = format_dataframe(df16)
    df16.to_sql(name="MF_m_02", con=engine, if_exists='replace', index=False)
    st.markdown(f"✅ **Data is Successfully Validated and Uploaded in the Database.")


st.title("Upload Data")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            process_send(df)

        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            process_send(df)
        else:
            raise ValueError("Invalid file format. Please upload a CSV or Excel file.")
    except ValueError as e:
        st.error(e)
