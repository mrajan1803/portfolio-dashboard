import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="₹1 Crore Equity Portfolio", 
    page_icon="📈", 
    layout="wide"
)

st.title("📈 ₹1 Crore Simulated Indian Equity Portfolio")
st.markdown("Live tracking of 15-stock allocation, P&L, and sector exposure.")

# 2. Read directly from the Public Google Sheet (Bypassing Secrets!)
# We use the specific GID for your Holdings tab: 1991889713
sheet_csv_url = "https://docs.google.com/spreadsheets/d/1OzqcT2AWsknaZceIe06ph0yn904YDp7BViqEErgCGEw/export?format=csv&gid=1991889713"

try:
    df_holdings = pd.read_csv(sheet_csv_url)
    df_holdings = df_holdings.dropna(subset=['Ticker']) # Remove empty rows
except Exception as e:
    st.error(f"Something went wrong reading the data: {e}")
    st.stop()

# 3. Clean and Calculate Data
numeric_cols = ['Shares Held', 'Average Buy Price (INR)', 'Target Weight (%)', 
                'Current Price (INR)', 'Market Value (INR)', 'Invested Cost (INR)', 'Unrealized P/L (INR)']

# Convert columns to numbers safely
for col in numeric_cols:
    if col in df_holdings.columns:
        df_holdings[col] = pd.to_numeric(df_holdings[col].astype(str).str.replace(r'[₹,%]', '', regex=True), errors='coerce').fillna(0)

total_invested = df_holdings['Invested Cost (INR)'].sum()
total_value = df_holdings['Market Value (INR)'].sum()
total_pnl = df_holdings['Unrealized P/L (INR)'].sum()
net_return = (total_pnl / total_invested) * 100 if total_invested > 0 else 0

# 4. Render KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Invested Cost", f"₹{total_invested:,.2f}")
with col2:
    st.metric("Current Market Value", f"₹{total_value:,.2f}", delta=f"₹{total_pnl:,.2f}")
with col3:
    st.metric("Unrealized P&L", f"₹{total_pnl:,.2f}")
with col4:
    st.metric("Net Return", f"{net_return:.2f}%")

st.divider()

# 5. Build Interactive Charts
st.subheader("Portfolio Composition")
chart_col1, chart_col2 = st.columns(2)

# Sector mapping
sector_mapping = {
    'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'RELIANCE': 'Energy & Retail',
    'BHARTIARTL': 'Telecom', 'LT': 'Industrials', 'SUNPHARMA': 'Healthcare',
    'TCS': 'IT', 'HCLTECH': 'IT', 'NTPC': 'Utilities', 'HINDUNILVR': 'FMCG',
    'MRF': 'Automotive', 'OBEROIRLTY': 'Real Estate', 'MPHASIS': 'IT Services',
    'REDINGTON': 'Distribution', 'ECLERX': 'IT Services'
}
df_holdings['Sector'] = df_holdings['Ticker'].map(sector_mapping)

with chart_col1:
    fig_sector = px.pie(
        df_holdings, 
        values='Market Value (INR)', 
        names='Sector', 
        title='Sector Allocation (by Market Value)',
        hole=0.4
    )
    st.plotly_chart(fig_sector, use_container_width=True)

with chart_col2:
    df_sorted = df_holdings.sort_values(by='Market Value (INR)', ascending=True)
    fig_bar = px.bar(
        df_sorted, 
        x='Market Value (INR)', 
        y='Ticker', 
        orientation='h',
        title='Current Market Value by Stock'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# 6. Live Holdings Data Table
st.subheader("Live Holdings Tracker")
display_df = df_holdings[['Ticker', 'Company Name', 'Sector', 'Shares Held', 
                          'Average Buy Price (INR)', 'Current Price (INR)', 
                          'Invested Cost (INR)', 'Market Value (INR)', 'Unrealized P/L (INR)']]

st.dataframe(
    display_df.style.format({
        'Average Buy Price (INR)': '₹{:,.2f}',
        'Current Price (INR)': '₹{:,.2f}',
        'Invested Cost (INR)': '₹{:,.2f}',
        'Market Value (INR)': '₹{:,.2f}',
        'Unrealized P/L (INR)': '₹{:,.2f}'
    }).map(lambda val: 'color: green' if val > 0 else 'color: red', subset=['Unrealized P/L (INR)']),
    use_container_width=True,
    hide_index=True
)
