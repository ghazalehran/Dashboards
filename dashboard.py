import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Page setup
st.set_page_config(page_title="Retail Profitability Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("superstore_cleaned.csv", parse_dates=["Order Date", "Ship Date"])

# Fix Discount Bin formatting (if needed)
df['Discount Bin'] = pd.Categorical(
    df['Discount Bin'],
    categories=['0%', '0–10%', '10–20%', '20–40%', '40–80%', '>80%'],
    ordered=True
)

# Add Loss Flag
df['Is Loss'] = df['Profit'] < 0

# Optional: Map state to code for Plotly
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

# Sidebar filters
st.sidebar.header("📊 Filters")
segment = st.sidebar.selectbox("Customer Segment", ["All"] + sorted(df['Segment'].unique()))
category = st.sidebar.selectbox("Product Category", ["All"] + sorted(df['Category'].unique()))
discount_bin = st.sidebar.selectbox("Discount Bin", ["All"] + sorted(df['Discount Bin'].dropna().unique()))

# Apply filters
filtered = df.copy()
if segment != "All":
    filtered = filtered[filtered['Segment'] == segment]
if category != "All":
    filtered = filtered[filtered['Category'] == category]
if discount_bin != "All":
    filtered = filtered[filtered['Discount Bin'] == discount_bin]

# Title + author
st.markdown("<h2 style='text-align:center;'>🛍️ Superstore Profitability Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Created by Ghazal Ran</p>", unsafe_allow_html=True)

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${filtered['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered['Profit'].sum():,.0f}")
margin = (filtered['Profit'].sum() / filtered['Sales'].sum() * 100) if filtered['Sales'].sum() else 0
col3.metric("Profit Margin", f"{margin:.2f}%")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💸 Discount Impact", "🔥 Loss Drilldown", "🗺️ Region Map"])

# ---- Tab 1: Overview ----
with tab1:
    st.subheader("Profit by Product Category")
    category_profit = filtered.groupby('Category')['Profit'].sum().sort_values()
    fig1, ax1 = plt.subplots()
    category_profit.plot(kind='bar', ax=ax1, color="#007acc")
    ax1.set_ylabel("Profit")
    ax1.set_title("")
    ax1.tick_params(axis='x', rotation=0)
    ax1.grid(axis='y')
    st.pyplot(fig1)

    st.subheader("Monthly Sales Trend")
    filtered['YearMonth'] = filtered['Order Date'].dt.to_period('M').astype(str)
    monthly = filtered.groupby('YearMonth')[['Sales', 'Profit']].sum()
    fig2, ax2 = plt.subplots()
    monthly.plot(ax=ax2)
    ax2.set_xlabel("Month")
    ax2.grid(True)
    st.pyplot(fig2)

# ---- Tab 2: Discount Impact ----
with tab2:
    st.subheader("Average Profit by Discount Level")
    avg_profit = filtered.groupby('Discount Bin')['Profit'].mean().dropna()
    fig3, ax3 = plt.subplots()
    avg_profit.plot(kind='bar', color="#ffa726", ax=ax3)
    ax3.set_ylabel("Average Profit")
    ax3.axhline(0, color='gray', linestyle='--')
    ax3.grid(True)
    st.pyplot(fig3)

    st.subheader("Loss Rate by Discount Level")
    loss_df = filtered.copy()
    loss_df['Is Loss'] = loss_df['Profit'] < 0
    loss_rate = loss_df.groupby('Discount Bin')['Is Loss'].mean().dropna() * 100
    fig4, ax4 = plt.subplots()
    loss_rate.plot(kind='bar', color="#ef5350", ax=ax4)
    ax4.set_ylabel("% Loss-Making Orders")
    ax4.axhline(50, color='gray', linestyle='--')
    ax4.grid(True)
    st.pyplot(fig4)

# ---- Tab 3: Loss Drilldown ----
with tab3:
    st.subheader("Loss Heatmap by Segment, Category, and Ship Mode")
    pivot = df[df['Profit'] < 0].pivot_table(
        index=['Segment', 'Category'],
        columns='Ship Mode',
        values='Profit',
        aggfunc='sum'
    ).fillna(0)
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Reds", ax=ax5)
    st.pyplot(fig5)

    st.subheader("Top 10 Loss-Making Combinations")
    loss_table = df[df['Profit'] < 0].groupby(['Segment', 'Category', 'Ship Mode']) \
        .agg(Loss_Orders=('Profit', 'count'), Avg_Loss=('Profit', 'mean'), Total_Loss=('Profit', 'sum')) \
        .sort_values(by='Total_Loss').round(2).head(10)
    st.dataframe(loss_table.style.background_gradient(cmap='Reds', subset=['Total_Loss']))

# ---- Tab 4: Region Map ----
with tab4:
    st.subheader("🗺️ Profit by State (U.S.)")

    # Group by state
    state_profit = df.groupby('State')['Profit'].sum().reset_index()

    # Map full state names to 2-letter codes
    state_profit['State Code'] = state_profit['State'].map(state_to_code)

    # Drop missing codes
    state_profit = state_profit.dropna(subset=['State Code'])

    # Build choropleth map
    fig_map = px.choropleth(
        state_profit,
        locations='State Code',
        locationmode='USA-states',
        color='Profit',
        color_continuous_scale='RdBu',
        scope='usa',
        labels={'Profit': 'Total Profit'},
        title=""
    )

    st.plotly_chart(fig_map, use_container_width=True)


# Footer
st.markdown("<hr><div style='text-align:center; font-size:13px; color:gray;'>© 2024 Ghazal Ran | Built with Streamlit</div>", unsafe_allow_html=True)
