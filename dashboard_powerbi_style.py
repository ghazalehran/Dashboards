import streamlit as st
import pandas as pd
import plotly.express as px

# ---- CONFIG ----
st.set_page_config(layout="wide", page_title="Retail Dashboard - Power BI Style")

# ---- LOAD DATA ----
df = pd.read_csv("superstore_cleaned.csv", parse_dates=["Order Date", "Ship Date"])
df['Is Loss'] = df['Profit'] < 0
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

# State code mapping
state_to_code = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
df['State Code'] = df['State'].map(state_to_code)

# ---- TITLE ----
st.markdown("""
    <style>
    .title {text-align:center; font-size:32px; font-weight:bold; margin-bottom:5px;}
    .subtitle {text-align:center; font-size:16px; color:gray; margin-bottom:20px;}
    .metric-block {text-align:center; padding:15px; border-radius:6px; background-color:#f4f4f4;}
    .metric-label {font-size:14px; color:gray;}
    .metric-value {font-size:26px; font-weight:bold;}
    </style>
    <div class='title'>📊 Superstore Profit Dashboard</div>
    <div class='subtitle'>One-page summary | Built by Ghazal Ran</div>
""", unsafe_allow_html=True)

# ---- ROW 1 ----
col1, col2, col3 = st.columns([1.2, 1.1, 0.7])

# 📍 Profit by State Map
with col1:
    state_profit = df.groupby('State')['Profit'].sum().reset_index()
    state_profit['State Code'] = state_profit['State'].map(state_to_code)
    fig1 = px.choropleth(
        state_profit,
        locations='State Code',
        locationmode='USA-states',
        color='Profit',
        color_continuous_scale='RdBu',
        scope='usa',
        title='',
    )
    st.plotly_chart(fig1, use_container_width=True)

# 📈 Monthly Profit Trend
with col2:
    monthly = df.groupby('YearMonth')['Profit'].sum().reset_index()
    fig2 = px.line(monthly, x='YearMonth', y='Profit', markers=True)
    fig2.update_layout(title='', xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig2, use_container_width=True)

# 💰 KPI: Total Profit
with col3:
    profit = df['Profit'].sum()
    margin = df['Profit'].sum() / df['Sales'].sum() * 100
    st.markdown(f"<div class='metric-block'><div class='metric-label'>Total Profit</div><div class='metric-value'>${profit:,.0f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-block'><div class='metric-label'>Profit Margin</div><div class='metric-value'>{margin:.1f}%</div></div>", unsafe_allow_html=True)

# ---- ROW 2 ----
col4, col5, col6 = st.columns(3)

# 📊 Profit by Category
with col4:
    cat_profit = df.groupby('Category')['Profit'].sum().reset_index()
    fig3 = px.bar(cat_profit, x='Profit', y='Category', orientation='h',
                  color='Category', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_layout(title='', xaxis_title=None, yaxis_title=None, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# 📊 Revenue vs Profit by Category
with col5:
    revenue_profit = df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    melted = revenue_profit.melt(id_vars='Category', value_vars=['Sales', 'Profit'], var_name='Metric', value_name='Amount')
    fig4 = px.bar(melted, x='Amount', y='Category', color='Metric', barmode='group',
                  orientation='h', color_discrete_sequence=['#1f77b4', '#2ca02c'])
    fig4.update_layout(title='', xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig4, use_container_width=True)

# 📉 Profit by Discount Bin
with col6:
    df['Discount Bin'] = pd.cut(df['Discount'], bins=[-0.01, 0, 0.1, 0.2, 0.4, 0.8, 1],
                                labels=['0%', '0–10%', '10–20%', '20–40%', '40–80%', '>80%'])
    avg_profit = df.groupby('Discount Bin')['Profit'].mean().reset_index().dropna()
    fig5 = px.bar(avg_profit, x='Discount Bin', y='Profit', color='Profit',
                  color_continuous_scale='RdBu')
    fig5.update_layout(title='', xaxis_title=None, yaxis_title=None, showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# ---- Footer ----
st.markdown("<hr><div style='text-align:center; font-size:12px; color:gray;'>© 2024 Ghazal Ran | Streamlit Dashboard</div>", unsafe_allow_html=True)
