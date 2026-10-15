import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="₹1 Cr Equity Portfolio", page_icon="📈", layout="wide")
st.title("📈 ₹1 Crore Quantitative Equity Portfolio")
st.markdown("Advanced analytics, risk metrics, and historical tracking.")

# 2. Fetch Live Holdings Data
sheet_csv_url = "https://docs.google.com/spreadsheets/d/1OzqcT2AWsknaZceIe06ph0yn904YDp7BViqEErgCGEw/export?format=csv&gid=1991889713"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(sheet_csv_url)
    df = df.dropna(subset=['Ticker'])
    
    numeric_cols = ['Shares Held', 'Average Buy Price (INR)', 'Target Weight (%)', 
                    'Current Price (INR)', 'Market Value (INR)', 'Invested Cost (INR)', 'Unrealized P/L (INR)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[₹,%]', '', regex=True), errors='coerce').fillna(0)
    
    df['Net Return (%)'] = (df['Unrealized P/L (INR)'] / df['Invested Cost (INR)']) * 100
    df['Net Return (%)'] = df['Net Return (%)'].fillna(0)
    
    meta_data = {
        'HDFCBANK': {'Sector': 'Financials', 'Cap': 'Large Cap'},
        'ICICIBANK': {'Sector': 'Financials', 'Cap': 'Large Cap'},
        'RELIANCE': {'Sector': 'Conglomerate', 'Cap': 'Large Cap'},
        'BHARTIARTL': {'Sector': 'Telecom', 'Cap': 'Large Cap'},
        'LT': {'Sector': 'Infrastructure', 'Cap': 'Large Cap'},
        'SUNPHARMA': {'Sector': 'Pharma', 'Cap': 'Large Cap'},
        'TCS': {'Sector': 'IT', 'Cap': 'Large Cap'},
        'HCLTECH': {'Sector': 'IT', 'Cap': 'Large Cap'},
        'NTPC': {'Sector': 'Energy', 'Cap': 'Large Cap'},
        'HINDUNILVR': {'Sector': 'FMCG', 'Cap': 'Large Cap'},
        'MRF': {'Sector': 'Auto', 'Cap': 'Large Cap'},
        'OBEROIRLTY': {'Sector': 'Realty', 'Cap': 'Mid Cap'},
        'MPHASIS': {'Sector': 'IT', 'Cap': 'Mid Cap'},
        'REDINGTON': {'Sector': 'IT', 'Cap': 'Small Cap'},
        'ECLERX': {'Sector': 'IT', 'Cap': 'Small Cap'}
    }
    
    df['Sector'] = df['Ticker'].apply(lambda x: meta_data.get(x, {}).get('Sector', 'Other'))
    df['Market Cap'] = df['Ticker'].apply(lambda x: meta_data.get(x, {}).get('Cap', 'Other'))
    
    return df

df_holdings = load_data()

# 3. Sidebar: Filters & Download
st.sidebar.header("🎛️ Portfolio Controls")

# Interactive Filters
selected_sectors = st.sidebar.multiselect("Filter by Sector", df_holdings['Sector'].unique(), default=df_holdings['Sector'].unique())
selected_caps = st.sidebar.multiselect("Filter by Market Cap", df_holdings['Market Cap'].unique(), default=df_holdings['Market Cap'].unique())

# Apply filters
df_filtered = df_holdings[(df_holdings['Sector'].isin(selected_sectors)) & (df_holdings['Market Cap'].isin(selected_caps))]

st.sidebar.divider()

# Download Executive Report
st.sidebar.subheader("📥 Executive Report")
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download Portfolio CSV",
    data=csv_data,
    file_name=f"Portfolio_Report_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)

# 4. Filtered KPIs
total_invested = df_filtered['Invested Cost (INR)'].sum()
total_value = df_filtered['Market Value (INR)'].sum()
total_pnl = df_filtered['Unrealized P/L (INR)'].sum()
overall_return = (total_pnl / total_invested) * 100 if total_invested > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Filtered Invested Cost", f"₹{total_invested:,.0f}")
kpi2.metric("Filtered Market Value", f"₹{total_value:,.0f}", delta=f"₹{total_pnl:,.0f}")
kpi3.metric("Filtered Unrealized P&L", f"₹{total_pnl:,.0f}")
kpi4.metric("Filtered Net Return", f"{overall_return:.2f}%")

st.divider()

# 5. Application Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Historical Trend", "⚖️ Risk Analytics", "🔍 Stock Screener"])

# --- TAB 1: OVERVIEW ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig_sec = px.pie(df_filtered, values='Market Value (INR)', names='Sector', title='Sector Exposure', hole=0.4)
        st.plotly_chart(fig_sec, use_container_width=True)
    with col2:
        fig_cap = px.pie(df_filtered, values='Market Value (INR)', names='Market Cap', title='Market Cap Exposure', hole=0.4)
        st.plotly_chart(fig_cap, use_container_width=True)
    
    st.dataframe(
        df_filtered[['Ticker', 'Company Name', 'Sector', 'Shares Held', 'Market Value (INR)', 'Unrealized P/L (INR)', 'Net Return (%)']].style.format({
            'Market Value (INR)': '₹{:,.0f}',
            'Unrealized P/L (INR)': '₹{:,.0f}',
            'Net Return (%)': '{:.2f}%'
        }).map(lambda val: 'color: #00C851' if val > 0 else 'color: #ff4444', subset=['Unrealized P/L (INR)', 'Net Return (%)']),
        use_container_width=True, hide_index=True
    )

# --- TAB 2: HISTORICAL TREND (YFinance) ---
@st.cache_data(ttl=3600)
def fetch_history(tickers):
    ns_tickers = [t + ".NS" for t in tickers]
    data = yf.download(ns_tickers, period="6mo", interval="1d")['Close']
    return data

with tab2:
    st.subheader("6-Month Portfolio Trend vs Nifty 50")
    with st.spinner("Fetching historical data from Yahoo Finance..."):
        try:
            tickers_list = df_holdings['Ticker'].tolist()
            hist_prices = fetch_history(tickers_list)
            
            # Simple Portfolio Simulation (Equal weight scaled to 100 for indexing)
            port_returns = hist_prices.pct_change().mean(axis=1)
            port_index = (1 + port_returns).cumprod() * 100
            
            # Fetch Nifty 50 Benchmark
            nifty = yf.download("^NSEI", period="6mo", interval="1d")['Close']
            nifty_index = (1 + nifty.pct_change()).cumprod() * 100
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=port_index.index, y=port_index, mode='lines', name='Simulated Portfolio', line=dict(color='#00C851', width=3)))
            fig_trend.add_trace(go.Scatter(x=nifty_index.index, y=nifty_index, mode='lines', name='Nifty 50 (Benchmark)', line=dict(color='#33B5E5', width=2, dash='dash')))
            fig_trend.update_layout(title="Indexed Growth (Base 100)", xaxis_title="Date", yaxis_title="Indexed Value", hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load historical data. Make sure market is open. Error: {e}")

# --- TAB 3: RISK ANALYTICS ---
with tab3:
    st.subheader("Quantitative Risk Metrics")
    st.markdown("Automated CAPM and Risk Profile calculation using 6-month daily variances.")
    
    try:
        daily_returns = hist_prices.pct_change().dropna()
        nifty_returns = nifty.pct_change().dropna()
        
        # Calculate Volatility (Standard Deviation Annualized)
        port_daily_ret = daily_returns.mean(axis=1) # Portfolio daily return
        ann_volatility = port_daily_ret.std() * np.sqrt(252) * 100
        
        # Calculate Beta
        cov_matrix = np.cov(port_daily_ret, nifty_returns)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        
        # Calculate Sharpe Ratio (Assuming 7% Risk-Free Rate)
        risk_free_rate = 0.07
        ann_return = port_daily_ret.mean() * 252
        sharpe_ratio = (ann_return - risk_free_rate) / (ann_volatility / 100)
        
        r1, r2, r3 = st.columns(3)
        r1.metric("Portfolio Beta (vs Nifty 50)", f"{beta:.2f}", delta="Ideal range: 0.8 - 1.2" if 0.8<=beta<=1.2 else "High Volatility", delta_color="off")
        r2.metric("Annualized Volatility", f"{ann_volatility:.2f}%")
        r3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}", help="Risk-adjusted return. > 1 is good.")
        
    except:
        st.info("Risk metrics will load once historical data is successfully fetched.")

# --- TAB 4: STOCK SCREENER ---
with tab4:
    st.subheader("Deep-Dive Fundamental Screener")
    selected_stock = st.selectbox("Select a stock to analyze:", df_holdings['Ticker'].tolist())
    
    if selected_stock:
        st.write(f"### Fetching Live Profile for {selected_stock}")
        try:
            stock = yf.Ticker(f"{selected_stock}.NS")
            info = stock.info
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            c2.metric("Market Cap (Cr)", f"₹{info.get('marketCap', 0) / 10000000:,.0f}" if info.get('marketCap') else 'N/A')
            c3.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A')
            c4.metric("52 Week High", f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}")
            
            # Mini chart
            hist = stock.history(period="3mo")
            fig_mini = px.line(hist, x=hist.index, y='Close', title=f"3-Month Price Trend: {selected_stock}")
            st.plotly_chart(fig_mini, use_container_width=True)
            
        except Exception as e:
            st.warning("Could not fetch fundamental data from Yahoo Finance at this time.")
