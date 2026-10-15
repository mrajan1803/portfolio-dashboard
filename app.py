import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(
    page_title="₹1 Crore Equity Portfolio", 
    page_icon="📈", 
    layout="wide"
)

st.title("📈 ₹1 Crore Simulated Indian Equity Portfolio")
st.markdown("Live tracking of 15-stock allocation, P&L, and sector exposure.")

# 2. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Read the 'Holdings' tab from your Google Sheet
    df_holdings = conn.read(worksheet="Holdings", usecols=list(range(9)))
    df_holdings = df_holdings.dropna(subset=['Ticker']) # Remove empty rows
except Exception as e:
    st.error("Could not read the Google Sheet. Please check your connection secrets and ensure the sheet is shared as 'Anyone with the link can view'.")
    st.stop()

# 3. Clean and Calculate Data
# Ensure numeric columns are strictly numeric by stripping currency symbols and commas
numeric_cols = ['Shares Held', 'Average Buy Price (INR)', 'Target Weight (%)', 
                'Current Price (INR)', 'Market Value (INR)', 'Invested Cost (INR)', 'Unrealized P/L (INR)']
for col in numeric_cols:
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

# Sector mapping based on your 15 chosen stocks
sector_mapping = {
    'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'RELIANCE': 'Energy & Retail',
    'BHARTIARTL': 'Telecom', 'LT': 'Industrials', 'SUNPHARMA': 'Healthcare',
    'TCS': 'IT', 'HCLTECH': 'IT', 'NTPC': 'Utilities', 'HINDUNILVR': 'FMCG',
    'MRF': 'Automotive', 'OBEROIRLTY': 'Real Estate', 'MPHASIS': 'IT Services',
    'REDINGTON': 'Distribution', 'ECLERX': 'IT Services'
}
df_holdings['Sector'] = df_holdings['Ticker'].map(sector_mapping)

with chart_col1:
    # Sector Allocation Donut Chart
    fig_sector = px.pie(
        df_holdings, 
        values='Market Value (INR)', 
        names='Sector', 
        title='Sector Allocation (by Market Value)',
        hole=0.4
    )
    st.plotly_chart(fig_sector, use_container_width=True)

with chart_col2:
    # Stock Value Bar Chart
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
