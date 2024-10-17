import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
  
# Main content
st.title('Mutual Fund Section')


# Create a 2x2 grid layout for visualizations
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Correct file path
file_path_mf2 = r"files/MF_m_02.csv"
df = pd.read_csv(file_path_mf2).iloc[-12:]
df['Net_AUM'] = df['Net_AUM'].str.replace(',', '', regex=False).apply(pd.to_numeric,errors='coerce')/ 1e5
df['No_Folios'] = df['No_Folios'].str.replace(',', '', regex=False).apply(pd.to_numeric,errors='coerce')/ 1e7

# Visualization 1: Bar Chart for Number of Orders by Quarter and Type
with col1:
    #st.subheader('Number of MF Folios (in Crore)')
    fig_folios = px.bar(
        df[['Month','No_Folios']],
        x='Month',
        y='No_Folios',
        text_auto='.2s',
        #color='TYPE',
        #barmode='group',
        title='Number of MF Folios (in Crore)'
    )
    # Add text annotations for starting and ending values (adjust position and formatting as needed)
    st.plotly_chart(fig_folios)

# Visualization 2: Penalty Applied Per Quarter
with col2:
    #st.subheader('MF AUM (in Rs Lakh Crore)')
    fig_AUM = px.bar(
        df[['Month','Net_AUM']],
        x='Month',
        y='Net_AUM',
        text_auto='.2s',
        #color='TYPE',
        #barmode='group',
        title='MF AUM (in Rs Lakh Crore)'

    )
    st.plotly_chart(fig_AUM)