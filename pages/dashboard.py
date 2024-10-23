import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import random
import plotly.express as px


def create_dummy_data():
    end_date = datetime.now().replace(day=1) - timedelta(days=1)
    dates = pd.date_range(end=end_date, periods=72, freq='M')
    
    np.random.seed(42)
    nifty = np.random.normal(1, 0.02, 72).cumprod() * 8000
    bonds = np.random.normal(1, 0.01, 72).cumprod() * 6000
    gold = np.random.normal(1, 0.015, 72).cumprod() * 5000
    silver = np.random.normal(1, 0.025, 72).cumprod() * 4000
    
    return pd.DataFrame({
        'Month': dates,
        'Nifty Index': nifty.round(2),
        'Government Bond Index': bonds.round(2),
        'Gold': gold.round(2),
        'Silver': silver.round(2)
    })

def calculate_cagr(first_value, last_value, num_years):
    """Calculate CAGR given first value, last value and number of years"""
    if first_value <= 0 or last_value <= 0:
        return 0
    return (((last_value / first_value) ** (1 / num_years)) - 1) * 100

def normalize_data(df):
    normalized_df = df.copy()
    for column in df.columns[1:]:
        first_value = normalized_df[column].iloc[0]
        normalized_df[column] = ((normalized_df[column] - first_value) / first_value) * 100
    return normalized_df

def generate_color_codes(elements):
  colors = {}
  for element in elements:
    # Generate a random hexadecimal color code
    color = f"#{random.randint(0, 0xFFFFFF):06x}"
    colors[element] = color
  return colors

def main():
    st.title('Market Returns Comparison')
    file_path_indices = r"files/market_data.csv"
    df = pd.read_csv(file_path_indices)
    df['Month'] = pd.to_datetime(df['Month'], format="%d-%m-%Y")
    assets_list = list(df.columns)[1:]
    #df = create_dummy_data()
    end_date = df['Month'].max()

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    period_options = ["3 Months", "6 Months", "9 Months", "1 Year", "5 Years", "10 Years", "15 Years", "20 Years", "Custom"]
    selected_period = st.radio("Select Period", period_options, horizontal=True)

    if selected_period == "Custom":
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=end_date - timedelta(days=365),
                min_value=df['Month'].min(),
                max_value=end_date
            )
        with col3:
            end_date = st.date_input(
                "End Date",
                value=end_date,
                min_value=start_date,
                max_value=df['Month'].max()
            )
    else:
        period_days = {
            "3 Months": 95,
            "6 Months": 185,
            "9 Months": 275,
            "1 Year": 370,
            "5 Years": 1830,
            "10 Years": 365*10+2+5,
            "15 Years": 365*15+3+5,
            "20 Years": 365*20+5+5,

        }
        start_date = end_date - timedelta(days=period_days[selected_period])
    

    if True:
        mask = (df['Month'] >= pd.Timestamp(start_date)) & (df['Month'] <= pd.Timestamp(end_date))
        filtered_df = df.loc[mask]
        normalized_df = normalize_data(filtered_df).reset_index(drop=True)

        first_date = filtered_df['Month'].min()
        last_date = filtered_df['Month'].max()
        num_years = (last_date - first_date).days / 365

        # Example usage
        colors = generate_color_codes(assets_list)

        # Create two columns
        col6, col7 = st.columns(2) 
        with col6:                    
            fig = go.Figure()
            for column in assets_list:
                first_value = normalized_df[column].iloc[0]
                last_value = normalized_df[column].iloc[-1]   
                fig.add_trace(
                    go.Scatter(
                        x=normalized_df['Month'],
                        y=normalized_df[column],
                        name=column,
                        line=dict(color=colors[column], width=2),
                        mode='lines'
                    )
                )

                fig.add_annotation(
                    x=normalized_df['Month'].iloc[-1],
                    y=last_value,
                    text=f"{column}, {last_value:.1f}%",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=colors[column],
                    font=dict(color=colors[column])
                )

            fig.update_layout(
                title={
                    'text': f'Absolute Returns ({first_date.strftime("%b %Y")} - {last_date.strftime("%b %Y")})',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20)
                },
                xaxis_title="",
                yaxis_title="Percentage Change (%)",
                hovermode='x unified',
                showlegend=False,
                plot_bgcolor='white',
                height=500,
                yaxis=dict(
                    gridcolor='lightgray',
                    zerolinecolor='lightgray',
                    tickformat='.1f',
                    ticksuffix='%'),
                xaxis=dict(tickformat='%b-%Y')
                )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("View & Download Data"):
                st.dataframe(normalized_df.round(2))
        
        with col7:                              
            fig = go.Figure()
            #st.subheader('CAGR')
            cagr_values = {}
            for column in assets_list:
                first_value = filtered_df[column].iloc[0]
                #st.write(f"{column},{first_value}")
                last_value = filtered_df[column].iloc[-1]
                cagr = calculate_cagr(first_value, last_value, num_years)
                cagr_values[column] = cagr
            
            cagr_data = pd.DataFrame.from_dict(cagr_values, orient='index', columns=['CAGR'])
            
            # Add bars
            for i, (asset, cagr) in enumerate(cagr_values.items()):
                fig.add_trace(
                    go.Bar(
                        name=asset,
                        x=[asset],
                        y=[cagr],
                        text=[f'{cagr:.1f}%'],
                        textposition='outside',
                        marker_color=colors[asset],
                        hovertemplate=f'{asset}<br>CAGR: %{{y:.1f}}%<extra></extra>',
                        textfont = dict(color=colors[asset])
                    )
                )

            # Update layout
            fig.update_layout(
                title={
                    'text': f'Annualised Returns (CAGR) ({first_date.strftime("%b %Y")} - {last_date.strftime("%b %Y")})',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20)
                },
                yaxis_title='CAGR (%)',
                showlegend=False,
                plot_bgcolor='white',
                height=500,
                yaxis=dict(
                    gridcolor='lightgray',
                    zerolinecolor='lightgray',
                    tickformat='.1f',
                    ticksuffix='%'
                ),
                xaxis=dict(
                    tickangle=0,
                    categoryorder='total descending'
                )
                #margin=dict(t=100, b=50, l=50, r=50)
            )

            # Add subtle grid lines
            #fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(211,211,211,0.5)')

            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            
            st.plotly_chart(fig, use_container_width=True)
                
            with st.expander("View &download data "):
                st.dataframe(pd.DataFrame(cagr_data))

    # Main content
    st.title('Mutual Funds Section')

    # Create a 2x2 grid layout for visualizations
    col8, col9 = st.columns(2)
    # Correct file path
    file_path_mf2 = r"files/MF_m_02.csv"
    df = pd.read_csv(file_path_mf2).iloc[-12:]
    df['Net_AUM'] = df['Net_AUM'].str.replace(',', '', regex=False).apply(pd.to_numeric,errors='coerce')/ 1e5
    df['No_Folios'] = df['No_Folios'].str.replace(',', '', regex=False).apply(pd.to_numeric,errors='coerce')/ 1e7

    # Visualization 1: Bar Chart for Number of Orders by Quarter and Type
    with col8:
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
    with col9:
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




if __name__ == "__main__":
    main()
