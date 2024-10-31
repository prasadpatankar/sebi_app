import streamlit as st
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
import os


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
  import numpy as np
  colors = {}
  for element in elements:
    # Generate a random hexadecimal color code
    color = f"#{np.random.randint(0, 0xFFFFFF):06x}"
    colors[element] = color
  return colors

def generate_colors(elements):
    colors_list = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF']
    color_index = 0
    colors = {}
    for element in elements:
        color = colors_list[color_index % len(colors_list)]
        colors[element] = color
        color_index += 1
    return colors

def generate_color_plotly(elements):
    import plotly.express as px
    colors = px.colors.qualitative.Plotly
    color_dict = {}
    for i, element in enumerate(elements):
        color_dict[element] = colors[i % len(colors)]
    return color_dict

def initialize_selected_assets(assets_list):
    """Initialize the selected assets in session state"""
    if 'selected_assets' not in st.session_state:
        # Select first three assets by default
        default_selected = assets_list[:3]
        st.session_state.selected_assets = default_selected

def handle_asset_selection():
    """Handle asset selection and enforce maximum 5 selections"""
    # Get current selections before updating
    previous_selections = set(st.session_state.selected_assets)
    current_selections = set()
    
    # Get new selections from all 
    assets_list = st.session_state.assets_list  # Get assets_list from session state
    for asset in assets_list:
        if st.session_state[f"checkbox_{asset}"]:
            current_selections.add(asset)
    
    # Handle the changes
    if len(current_selections) > 5:
        # Find the newly added asset
        new_asset = (current_selections - previous_selections).pop()
        # Revert the change
        st.session_state[f"checkbox_{new_asset}"] = False
        st.session_state.selected_assets = list(previous_selections)
        st.warning("⚠️ Please deselect an asset before selecting a new one (maximum 5 selections allowed)")
    else:
        st.session_state.selected_assets = list(current_selections)

def load_dataset(filename):
    """Load the dataset from the given filename"""
    import pandas as pd
    df = pd.read_csv(filename).iloc[:-1]
    df['Month'] = pd.to_datetime(df['Month'])
    df.sort_values(by="Month", inplace=True)
    assets_list = list(df.columns)[1:]
    return df, assets_list

def to_financial_year(date):
  if date.month <= 3:  # January to March falls in the previous FY
    financial_year = f"{date.year - 1}-{str(date.year)[2:]}"
  else:  # April to December falls in the current FY
    financial_year = f"{date.year}-{str(date.year + 1)[2:]}"

  return financial_year


st.title('Market Returns & CAGR')
# Load and process all datasets
dataset_files = ['Global Indices', 'Commodities_Currency', 'India Sectoral Indices']


# Allow user to select dataset
selected_dataset = st.selectbox('Select Dataset', dataset_files, index=0)

filepath = os.path.join("files", f"{selected_dataset}.csv")
# Load the selected dataset

df, assets_list = load_dataset(filepath)
# Store assets_list in session state for access in handle_asset_selection

#st.session_state.df = df
#df = create_dummy_data()
end_date = df['Month'].max()

# Create sidebar for asset selection
st.write("Select Assets (Max 5)")

# Initialize selected assets if not already done
initialize_selected_assets(assets_list)

st.session_state.df = df
st.session_state.assets_list = assets_list

# Add selection counter with color coding
selection_count = len(st.session_state.selected_assets)
count_color = "red" if selection_count >= 5 else "green"

if selection_count >=5:
    st.warning("⚠️ Please deselect an asset before selecting a new one (maximum 5 selections allowed)")

# Create rows of checkboxes (5 per row)
num_assets = len(assets_list)
num_rows = (num_assets + 6) // 7  # Round up division
num_cols = 7
for row in range(num_rows):
    # Create 5 columns for each row
    cols = st.columns(num_cols)
    
    # Add checkboxes to each column
    for col_idx in range(num_cols):
        asset_idx = row * num_cols + col_idx
        
        # Check if we still have assets to display
        if asset_idx < num_assets:
            asset = assets_list[asset_idx]
            disabled = (selection_count >= 5 and asset not in st.session_state.selected_assets)
            
            with cols[col_idx]:
                st.checkbox(
                    asset,
                    value=asset in st.session_state.selected_assets,
                    key=f"checkbox_{asset}",
                    on_change=handle_asset_selection,
                    disabled=disabled
                )

new_assets = st.session_state.selected_assets

if new_assets[0] not in assets_list:
    # Select first three assets by default
    print("hello")
    default_selected = assets_list[:3]
    st.session_state.selected_assets = default_selected
    initialize_selected_assets(assets_list)
    new_assets = st.session_state.selected_assets

period_options = ["3 Months", "6 Months", "9 Months", "1 Year", "5 Years", "10 Years", "15 Years", "20 Years", "Custom"]
selected_period = st.radio("Select Period", period_options, index=3, horizontal=True)

col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

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
    filtered_df.columns = [x.replace(" Index","\nIndex") for x in list(filtered_df.columns)]
    normalized_df = normalize_data(filtered_df).reset_index(drop=True)
    first_date = filtered_df['Month'].min()
    last_date = filtered_df['Month'].max()
    num_years = (last_date - first_date).days / 365

    # Example usage
    colors = generate_color_plotly(new_assets)

    # Create two columns
    col6, col7 = st.columns([6, 4]) 
    with col6:                    
        fig = go.Figure()
        for column in new_assets:
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
                font=dict(color=colors[column], size=20),
                ax=30
            )

        fig.update_layout(
            title={
                'text': f'Absolute Returns ({first_date.strftime("%b %Y")} - {last_date.strftime("%b %Y")})',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'right',
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
        st.write(f"Notes: data updated till {end_date.strftime(format="%B %d, %Y")}")
        with st.expander("View & Download Data"):
            st.dataframe(normalized_df.round(2))
    
    with col7:                              
        
        fig = go.Figure()
        #st.subheader('CAGR')
        cagr_values = {}
        for column in new_assets:
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
                    textfont = dict(color=colors[asset], size=20)
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
                range=[1.02*min(cagr_data['CAGR'])-5, 1.02*max(cagr_data['CAGR']) + 5],
                gridcolor='lightgray',
                zerolinecolor='lightgray',
                tickformat='.1f',
                ticksuffix='%',
            ),
            xaxis=dict(
                tickangle=0,
                categoryorder='total descending'
            ),
            #margin=dict(t=95, b=95, l=100, r=100)
        )

        # Add subtle grid lines
        #fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(211,211,211,0.5)')

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Notes: data updated till {end_date.strftime(format="%B %d, %Y")}")   
        with st.expander("View &download data "):
            st.dataframe(cagr_data)

# Main content
st.title('FPI Section')

# Create radio buttons using st.radio
param2 = "INR"
param1_options = ['Month', 'Financial Year', 'Calendar Year']
param2_options = ['USD', 'INR']
param1 = st.radio('Select Time Period', param1_options, index=1)
param2 = st.radio('Select Currency', param2_options, index=1)

file_path_fpi = r"files/dash_fpi.csv"
df1 = pd.read_csv(file_path_fpi)[:-1]
df1['Month1'] = pd.to_datetime(df1["Month"])
last_date = df1['Month1'].max()
df1['Month'] = df1['Month1']  + MonthEnd(0)
df1= df1.drop("Month1", axis=1)
all_fpi_cols = list(df1.columns)[1:]
df1['Financial Year'] = df1['Month'].apply(to_financial_year)            
df1['Calendar Year'] = df1['Month'].dt.year 

text2 = None
if param2=="USD":
    text2 = "(Amount in USD Million)"
else:
    text2 = "(Amount in Rupees Crore)"
df2= pd.DataFrame()
# Filter DataFrame based on parameters
if param1 == 'Month':
    df2 = df1.groupby(['Month'])[all_fpi_cols].sum().reset_index()
elif param1 == 'Financial Year':
    # Implement logic to group by financial year
    df2 = df1.groupby(['Financial Year'])[all_fpi_cols].sum().reset_index()
elif param1 == 'Calendar Year':
    df2 = df1.groupby(['Calendar Year'])[all_fpi_cols].sum().reset_index()

col10, col11 = st.columns(2)
with col10:
    if param2=="INR":
        selected_columns =  [col for col in all_fpi_cols if ('Equity' in col) and ("INR" in col)] 
    else:
        selected_columns =  [col for col in all_fpi_cols if ('Equity' in col) and ("USD" in col)] 
    selected_columns_all = [param1] +  selected_columns

    df2a= df2.iloc[-13:]
    x_values = df2a[param1].astype('str')
    y_values = df2a[selected_columns[0]]

    fig4 = go.Figure()
    fig4.add_trace(
        go.Bar(
            x=x_values,
            y=y_values,
            name=column,
            marker_color="darkgreen",
            text=np.round(y_values,0),
            textposition='outside',
            textfont = dict(color="darkgreen", size=15)
        ))
    fig4.update_layout(
        title={
            'text': f'Trends in FPI Investment- Equity\n {text2}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        showlegend=False,
        plot_bgcolor='white',
        height=500,
        yaxis=dict(
        range=[1.15*min(y_values), 1.15*max(y_values)],

        gridcolor='lightgray',
        zerolinecolor='lightgray',
        tickformat='.1f'),
        xaxis_title="",
        #yaxis_title="Amount"
        )
    st.plotly_chart(fig4, use_container_width=True)
    st.write(f"Notes: data updated till {last_date.strftime(format="%B %d, %Y")}")
    with st.expander("View &download data "):
        st.dataframe(df2)

with col11:
    if param2=="INR":
        selected_columns =  [col for col in all_fpi_cols if ('Debt' in col) and ("INR" in col)] 
    else:
        selected_columns =  [col for col in all_fpi_cols if ('Debt' in col) and ("USD" in col)] 
    selected_columns_all = [param1] +  selected_columns

    df2b= df2.iloc[-13:]
    x_values = df2b[param1].astype('str')
    y_values = df2b[selected_columns[0]]

    fig5 = go.Figure()
    fig5.add_trace(
        go.Bar(
            x=x_values,
            y=y_values,
            name=column,
            marker_color="royalblue",
            text=np.round(y_values,0),
            textposition='outside',
            textfont = dict(color="royalblue", size=15)
        ))
    fig5.update_layout(
        title={
            'text': f'Trends in FPI Investment- Debt\n {text2}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        showlegend=False,
        plot_bgcolor='white',
        height=500,
        yaxis=dict(
        range=[1.15*min(y_values), 1.15*max(y_values)],
        
        gridcolor='lightgray',
        zerolinecolor='lightgray',
        tickformat='.1f'),
        xaxis_title="",
        #yaxis_title="Amount"
        )
    st.plotly_chart(fig5, use_container_width=True)
    st.write(f"Notes: data updated till {last_date.strftime(format="%B %d, %Y")}")
    with st.expander("View &download data "):
        st.dataframe(df2)


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
  # Standard title with formatting
  #st.subheader('Number of MF Folios (in Crore)')
  # Create Figure with similar elements as fig5
  fig_folios = go.Figure()
  fig_folios.add_trace(
      go.Bar(
          x=df['Month'],
          y=df['No_Folios'],
          name='Number of Folios',  # Consistent naming
          marker_color=px.colors.qualitative.Bold[2],
          text=np.round(df['No_Folios'], 1),  # Text for data points
          textposition='outside',
          textfont=dict(color="royalblue", size=15)
      )
  )

  # Update layout with similar properties
  fig_folios.update_layout(
      title={
          'text': 'Number of MF Folios (in Crore)',
          'y': 0.95,
          'x': 0.5,
          'xanchor': 'right',
          'yanchor': 'top',
          'font': dict(size=20)
      },
      showlegend=False,  # Remove legend since there's only one trace
      plot_bgcolor='white',
      height=500,
      yaxis=dict(
          range=[ min(df['No_Folios'])-3,  max(df['No_Folios'])+2],  # Adjust based on data
          gridcolor='lightgray',
          zerolinecolor='lightgray',
          tickformat='.1f'
      ),
      xaxis_title="",
      #yaxis_title="Amount"
  )
  st.plotly_chart(fig_folios)

# Visualization 1: Bar Chart for Number of Orders by Quarter and Type
with col9:
  # Standard title with formatting
  #st.subheader('Number of MF Folios (in Crore)')
  # Create Figure with similar elements as fig5
  fig_AUM = go.Figure()
  fig_AUM.add_trace(
      go.Bar(
          x=df['Month'],
          y=df['Net_AUM'],
          name='AUM',  # Consistent naming
          marker_color=px.colors.qualitative.Bold[4],
          text=np.round(df['Net_AUM'], 1),  # Text for data points
          textposition='outside',
          textfont=dict(color="royalblue", size=15)
      )
  )

  # Update layout with similar properties
  fig_AUM.update_layout(
      title={
          'text': 'MF AUM (in Rs Lakh Crore)',
          'y': 0.95,
          'x': 0.5,
          'xanchor': 'right',
          'yanchor': 'top',
          'font': dict(size=20)
      },
      showlegend=False,  # Remove legend since there's only one trace
      plot_bgcolor='white',
      height=500,
      yaxis=dict(
          range=[ min(df['Net_AUM'])-3,  max(df['Net_AUM'])+2],  # Adjust based on data
          gridcolor='lightgray',
          zerolinecolor='lightgray',
          tickformat='.1f'
      ),
      xaxis_title="",
      #yaxis_title="Amount"
  )
  st.plotly_chart(fig_AUM)

