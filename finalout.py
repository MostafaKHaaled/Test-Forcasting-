import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

# st.header("this is Financial Report 💵💲")    
st.markdown("<h1 style='text-align: center;'>Financial Forcasting Report 💵💲</h1>", unsafe_allow_html=True)

df = pd.read_excel('Target by branch.xlsx' , sheet_name="Sheet1")
month_corrections = {
    'Septamper': 'September',
    'Desember': 'December',
    'january': 'January',
    'june': 'June',
    'septemper': 'September',
    'october': 'October',
    'Novamber': 'November',
    'Decamber': 'December',
    'Januray': 'January',
    'Fabruary': 'February',
    'septamber': 'September',
    'Septamer': 'September'
}

def correct_month(merged_str):
    """Correct misspelled month names."""
    for wrong, right in month_corrections.items():
        merged_str = merged_str.replace(wrong, right)
    return merged_str

# Apply corrections
df['Merged_corrected'] = df['Merged'].apply(correct_month)
df['Date'] = pd.to_datetime(df['Merged_corrected'].str.replace('-', ' '), format='%Y %B')

# Sidebar filters
st.sidebar.header("Filters")

selected_sections = st.sidebar.multiselect(
    "Select Name sections",
    options=sorted(df['Name section'].unique()),
    default=sorted(df['Name section'].unique())
)

selected_branches = st.sidebar.multiselect(
    "Select Branches",
    options=sorted(df['Branch'].unique()),
    default=sorted(df['Branch'].unique())
)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start date", value=df['Date'].min().date(), min_value=df['Date'].min().date(), max_value=df['Date'].max().date())
with col2:
    end_date = st.date_input("End date", value=df['Date'].max().date(), min_value=df['Date'].min().date(), max_value=df['Date'].max().date())

# Apply filters
filtered_df = df[
    (df['Name section'].isin(selected_sections)) &
    (df['Branch'].isin(selected_branches)) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
]

# Forecasting Section
st.sidebar.subheader("Forecasting")
forecast_branch = st.sidebar.selectbox(
    "Select Branch for Forecast",
    options=sorted(df['Branch'].unique()),
    index=0
)
forecast_section = st.sidebar.selectbox(
    "Select Section for Forecast",
    options=sorted(df['Section'].unique()),
    index=0
)
forecast_steps = st.sidebar.slider("Forecast Steps (Months)", min_value=1, max_value=6, value=2)

# Prepare data for forecast
forecast_filtered = df[
    (df['Branch'] == forecast_branch) &
    (df['Section'] == forecast_section) &
    (df['Date'] <= pd.to_datetime(end_date))
].copy()

forecast_filtered = forecast_filtered.sort_values('Date').set_index('Date')
ts = forecast_filtered['Total'].dropna()

st.divider()#''' ********************************* '''
########################################################################
branch_totals = filtered_df.groupby('Branch')['Total'].sum().reset_index()

fig = px.bar(
    branch_totals,
    x="Branch",
    y="Total",
    title="Total by Branch (in Millions)",
    text="Total"
)

fig.update_traces(
    texttemplate='%{text:.2s}',  # Auto-format (1M, 2M, etc.)
    textposition='outside',
    textfont_size=14
)

# Format y-axis to show millions
fig.update_yaxes(
    title_text="Total (Millions)",
    tickformat='.2s'  # SI prefix notation
)

st.plotly_chart(fig)
#########################################################################
#branch

df_cumulative_b = filtered_df.groupby(['Date', 'Branch'])['Total'].sum().unstack().cumsum()
df_cumulative_reset_b = df_cumulative_b.reset_index()
df_long_b = df_cumulative_reset_b.melt(id_vars='Date', var_name='Branch', value_name='Total')

# Name section
df_cumulative_s = filtered_df.groupby(['Date', 'Name section'])['Total'].sum().unstack().cumsum()
df_cumulative_reset_s = df_cumulative_s.reset_index()
df_long_s = df_cumulative_reset_s.melt(id_vars='Date', var_name='Name section', value_name='Total')


left, right = st.columns(2)

with left:
    fig_top = px.line(
        df_long_b,
        x='Date',
        y='Total',
        color='Branch',
        title='Total by Branch Over Time',
        markers=True      # optional, shows points

    )
    
    fig_top.update_traces(textposition='top center')
    st.plotly_chart(fig_top, use_container_width=True, key="Total by Branch Over Time")

with right:
    fig_bottom = px.line(
        df_long_s,
        x='Date',
        y='Total',
        color='Name section',
        title='Total by Section Over Time',
        markers=True
    )
    fig_bottom.update_traces(textposition='top center')
    st.plotly_chart(fig_bottom, use_container_width=True, key="Total by Section Over Time")

##################################################################################

SECt = filtered_df.groupby('Name section')['Total'].sum().sort_values(ascending=False).head(5).reset_index()


SECb = filtered_df.groupby('Name section')['Total'].sum().sort_values(ascending=True).head(5).reset_index()


left, right = st.columns(2)


with left:
    fig_top = px.bar(
        SECt, 
        x='Name section',
        y='Total',
        title='Top 5 Sections by Total',
        text_auto=True,
        height=400,
        color_discrete_sequence=['#2ecc71']
    )
    fig_top.update_traces(textposition='outside')
    st.plotly_chart(fig_top, use_container_width=True, key="top_5_chart")


with right:
    fig_bottom = px.bar(
        SECb, 
        x='Name section',
        y='Total',
        title='Bottom 5 Sections by Total',
        text_auto=True,
        height=400,
        color_discrete_sequence=['#e74c3c']
    )
    fig_bottom.update_traces(textposition='outside')
    st.plotly_chart(fig_bottom, use_container_width=True, key="bottom_5_chart")

###################################################################
# New Graphs: Total, Target, Branch over Date

st.header("Trends Over Time")

# 1. Total over Date
total_over_time = filtered_df.groupby('Date')['Total'].sum().reset_index()
fig_total = px.line(
    total_over_time, 
    x='Date', 
    y='Total', 
    title='Total Over Time',
    markers=True
)
fig_total.update_yaxes(title_text="Total (Millions)", tickformat='.2s')
st.plotly_chart(fig_total, use_container_width=True)

# 2. Target over Date
target_over_time = filtered_df.groupby('Date')['Target'].sum().reset_index()
fig_target = px.line(
    target_over_time, 
    x='Date', 
    y='Target', 
    title='Target Over Time',
    markers=True
)
fig_target.update_yaxes(title_text="Target (Millions)", tickformat='.2s')
st.plotly_chart(fig_target, use_container_width=True)

# 3. Total by Branch over Date
df_by_branch_date = filtered_df.groupby(['Date', 'Branch'])['Total'].sum().reset_index()
fig_branch = px.line(
    df_by_branch_date, 
    x='Date', 
    y='Total', 
    color='Branch', 
    title='Total by Branch Over Time',
    markers=True
)
fig_branch.update_yaxes(title_text="Total (Millions)", tickformat='.2s')
st.plotly_chart(fig_branch, use_container_width=True)

# Forecasting Output
st.header("ARIMA Forecasting")

if len(ts) < 10:
    st.warning(f"Only {len(ts)} data points for {forecast_branch}, Section {forecast_section}. Need more for reliable forecast.")
else:
    # Fit ARIMA(1,1,1) model
    model = ARIMA(ts, order=(1, 1, 1))
    fitted_model = model.fit()

    # Forecast
    forecast = fitted_model.forecast(steps=forecast_steps)
    forecast_dates = pd.date_range(start=ts.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')

    # Prepare forecast DataFrame
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Total': forecast,
        'Type': 'Forecast'
    })

    # Historical DataFrame (last points, but for chart use all)
    historical_df = pd.DataFrame({
        'Date': ts.index,
        'Total': ts.values,
        'Type': 'Historical'
    })

    # Combine for chart
    combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)

    # Line Chart
    fig_forecast = px.line(
        combined_df,
        x='Date',
        y='Total',
        color='Type',
        title=f'Forecast for {forecast_branch} Branch, Section {forecast_section}',
        markers=True
    )
    fig_forecast.update_yaxes(title_text="Total")
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Table: Last 5 Historical + Forecast
    last_historical = historical_df.tail(5)
    forecast_display = forecast_df[['Date', 'Total']].copy()
    forecast_display['Total'] = forecast_display['Total'].round(2)
    forecast_display['Date'] = forecast_display['Date'].dt.strftime('%Y-%B')
    last_historical['Date'] = last_historical['Date'].dt.strftime('%Y-%B')
    last_historical['Total'] = last_historical['Total'].round(2)

    combined_table = pd.concat([last_historical[['Date', 'Total']], forecast_display], ignore_index=True)
    combined_table['Type'] = ['Historical'] * 5 + ['Forecast'] * forecast_steps

    st.subheader("Data Table")
    st.dataframe(combined_table)

    st.info(f"Data points used: {len(ts)}")