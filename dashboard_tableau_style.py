import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Set wide layout
st.set_page_config(layout="wide", page_title="Retail Dashboard - Tableau Style")

# Load data
df = pd.read_csv("superstore_cleaned.csv", parse_dates=["Order Date", "Ship Date"])

# Map state names to abbreviations for Plotly
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

# Feature prep
df['Is Loss'] = df['Profit'] < 0
df['Discount Bin'] = pd.Categorical(
    df['Discount Bin'],
    categories=['0%', '0–10%', '10–20%', '20–40%', '40–80%', '>80%'],
    ordered=True
)
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

# ---- HEADER ----
st.markdown("""
    <style>
        .main-title {text-align: center; font-size: 36px; font-weight: 600; margin-bottom: 0px;}
        .author {text-align: center; color: gray; margin-top: 0px; margin-bottom: 20px;}
        .kpi-box {background-color: #f9f9f9; padding: 25px; border-radius: 8px; text-align: center; margin: 10px;}
        .kpi-number {font-size: 28px; font-weight: bold;}
        .kpi-label {font-size: 14px; color: #777;}
    </style>
    <div class='main-title'>📊 Superstore Profitability Dashboard</div>
    <div class='author'>by Ghazal Ran</div>
""", unsafe_allow_html=True)

# ---- KPIs ----
total_sales = f"${df['Sales'].sum():,.0f}"
total_profit = f"${df['Profit'].sum():,.0f}"
margin = df['Profit'].sum() / df['Sales'].sum() * 100
profit_margin = f"{margin:.2f}%"

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='kpi-box'><div class='kpi-number'>{total_sales}</div><div class='kpi-label'>Total Sales</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi-box'><div class='kpi-number'>{total_profit}</div><div class='kpi-label'>Total Profit</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='kpi-box'><div class='kpi-number'>{profit_margin}</div><div class='kpi-label'>Profit Margin</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ---- ROW 1: Category + Segment ----
col4, col5 = st.columns(2)

with col4:
    st.subheader("Profit by Category")
    cat_profit = df.groupby('Category')['Profit'].sum()
    fig1, ax1 = plt.subplots()
    cat_profit.plot(kind='bar', color="#1f77b4", ax=ax1)
    ax1.set_ylabel("Profit")
    ax1.set_xlabel("")
    ax1.tick_params(axis='x', rotation=0)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig1)

with col5:
    st.subheader("Profit by Segment")
    seg_profit = df.groupby('Segment')['Profit'].sum()
    fig2, ax2 = plt.subplots()
    seg_profit.plot(kind='bar', color="#ff7f0e", ax=ax2)
    ax2.set_ylabel("Profit")
    ax2.set_xlabel("")
    ax2.tick_params(axis='x', rotation=0)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig2)

# ---- ROW 2: Discount Analysis ----
col6, col7 = st.columns(2)

with col6:
    st.subheader("Avg Profit by Discount Bin")
    avg_profit = df.groupby('Discount Bin')['Profit'].mean().dropna()
    fig3, ax3 = plt.subplots()
    avg_profit.plot(kind='bar', color="#2ca02c", ax=ax3)
    ax3.axhline(0, linestyle='--', color='gray')
    ax3.set_ylabel("Avg Profit")
    ax3.tick_params(axis='x', rotation=0)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig3)

with col7:
    st.subheader("% Loss-Making Orders by Discount Bin")
    loss_rate = df.groupby('Discount Bin')['Is Loss'].mean().dropna() * 100
    fig4, ax4 = plt.subplots()
    loss_rate.plot(kind='bar', color="#d62728", ax=ax4)
    ax4.axhline(50, linestyle='--', color='gray')
    ax4.set_ylabel("% Loss Orders")
    ax4.tick_params(axis='x', rotation=0)
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig4)

# ---- ROW 3: Profit Trend + State Map ----
col8, col9 = st.columns(2)

with col8:
    st.subheader("Monthly Profit Trend")
    monthly = df.groupby('YearMonth')[['Profit']].sum()
    fig5, ax5 = plt.subplots()
    monthly.plot(ax=ax5, color="#9467bd", legend=False)
    ax5.set_ylabel("Profit")
    ax5.set_xlabel("Month")
    ax5.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig5)

with col9:
    st.subheader("Profit by U.S. State")
    state_profit = df.groupby('State')['Profit'].sum().reset_index()
    state_profit['State Code'] = state_profit['State'].map(state_to_code)
    fig6 = px.choropleth(state_profit,
                         locations='State Code',
                         locationmode='USA-states',
                         color='Profit',
                         color_continuous_scale='RdBu',
                         scope='usa',
                         labels={'Profit': 'Total Profit'})
    st.plotly_chart(fig6, use_container_width=True)

# ---- ROW 4: Loss Table ----
st.subheader("Top 10 Loss-Making Combinations")
loss_table = df[df['Is Loss']].groupby(['Segment', 'Category', 'Ship Mode']) \
    .agg(Loss_Orders=('Profit', 'count'), Avg_Loss=('Profit', 'mean'), Total_Loss=('Profit', 'sum')) \
    .sort_values(by='Total_Loss') \
    .round(2).head(10).reset_index()

st.dataframe(loss_table.style.background_gradient(cmap='Reds', subset=['Total_Loss']))

# ---- Footer ----
st.markdown("<hr><div style='text-align:center; font-size:12px; color:gray;'>© 2024 Ghazal Ran | Tableau-Style Streamlit Dashboard</div>", unsafe_allow_html=True)
