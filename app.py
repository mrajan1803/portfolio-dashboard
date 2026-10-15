import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="₹1 Cr Equity Portfolio", page_icon="📈", layout="wide")

# Custom CSS for an Executive Dark Dashboard Look
st.markdown("""
    <style>
        /* Hide Streamlit default branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Style the Metric Cards for Dark Theme */
        div[data-testid="stMetric"] {
            background-color: #1a1c24;
            border: 1px solid #2b2e3b;
            border-left: 4px solid #1c83e1;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-left: 4px solid #00C851;
            background-color: #21242f;
        }
        
        /* Clean up Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1a1c24;
            border-radius: 8px;
            padding: 5px 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px 4px 0px 0px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-weight: 600;
        }
        
        /* General Spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Quantitative Equity Portfolio")
st.markdown("**₹1 Crore Simulated Asset Allocation & Risk Analytics** | *Live Market Data*")
st.divider()

# ==========================================
# 2. FETCH LIVE DATA (Bypassing Secrets)
# ==========================================
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

try:
    df_holdings = load_data()
except Exception as e:
    st.error("Failed to load data from Google Sheets. Ensure the link is correct and public.")
    st.stop()

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.header("🎛️ Portfolio Controls")
    st.markdown("Filter the dashboard views:")
    
    selected_sectors = st.multiselect("Sector Allocation", df_holdings['Sector'].unique(), default=df_holdings['Sector'].unique())
    selected_caps = st.multiselect("Market Capitalization", df_holdings['Market Cap'].unique(), default=df_holdings['Market Cap'].unique())
    
    df_filtered = df_holdings[(df_holdings['Sector'].isin(selected_sectors)) & (df_holdings['Market Cap'].isin(selected_caps))]
    
    st.divider()
    st.subheader("📥 Export Data")
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Executive Report (CSV)",
        data=csv_data,
        file_name=f"Portfolio_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================
# 4. TOP KPI CARDS
# ==========================================
total_invested = df_filtered['Invested Cost (INR)'].sum()
total_value = df_filtered['Market Value (INR)'].sum()
total_pnl = df_filtered['Unrealized P/L (INR)'].sum()
overall_return = (total_pnl / total_invested) * 100 if total_invested > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Invested Capital", f"₹{total_invested:,.0f}")
kpi2.metric("Current Value", f"₹{total_value:,.0f}", delta=f"₹{total_pnl:,.0f}")
kpi3.metric("Unrealized P&L", f"₹{total_pnl:,.0f}")
kpi4.metric("Net Return", f"{overall_return:.2f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. MAIN DASHBOARD TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Allocation Overview", "📈 Historical Trend", "⚖️ Risk Analytics", "🔍 Stock Screener"])

# --- TAB 1: OVERVIEW ---
with tab1:
    col1, col2 = st.columns(2)
    
    def apply_premium_layout(fig):
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=40, l=0, r=0),
            font=dict(size=14, color="#fafafa")
        )
        return fig

    with col1:
        fig_sec = px.pie(df_filtered, values='Market Value (INR)', names='Sector', 
                         title='Sector Exposure', hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sec.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(apply_premium_layout(fig_sec), use_container_width=True)
        
    with col2:
        fig_cap = px.pie(df_filtered, values='Market Value (INR)', names='Market Cap', 
                         title='Market Cap Exposure', hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_cap.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(apply_premium_layout(fig_cap), use_container_width=True)
    
    st.subheader("Live Portfolio Ledger")
    st.dataframe(
        df_filtered[['Ticker', 'Company Name', 'Sector', 'Shares Held', 'Market Value (INR)', 'Unrealized P/L (INR)', 'Net Return (%)']].style.format({
            'Market Value (INR)': '₹{:,.0f}',
            'Unrealized P/L (INR)': '₹{:,.0f}',
            'Net Return (%)': '{:.2f}%'
        }).map(lambda val: 'color: #00C851; font-weight: bold' if val > 0 else 'color: #ff4444; font-weight: bold', subset=['Unrealized P/L (INR)', 'Net Return (%)']),
        use_container_width=True, hide_index=True
    )

# --- TAB 2: HISTORICAL TREND ---
@st.cache_data(ttl=3600)
def fetch_history(tickers):
    ns_tickers = [t + ".NS" for t in tickers]
    return yf.download(ns_tickers, period="6mo", interval="1d")['Close']

@st.cache_data(ttl=3600)
def fetch_nifty():
    return yf.download("^NSEI", period="6mo", interval="1d")['Close']

with tab2:
    st.subheader("6-Month Portfolio Trend vs Nifty 50")
    with st.spinner("Fetching historical market data..."):
        try:
            tickers_list = df_holdings['Ticker'].tolist()
            hist_prices = fetch_history(tickers_list).ffill().dropna(axis=1, how='all')
            nifty = fetch_nifty()
            
            port_returns = hist_prices.pct_change().mean(axis=1)
            port_index = (1 + port_returns).cumprod() * 100
            nifty_index = (1 + nifty.pct_change()).cumprod() * 100
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=port_index.index, y=port_index, mode='lines', name='Simulated Portfolio', 
                                           line=dict(color='#00C851', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(0, 200, 81, 0.1)'))
            
            nifty_series = nifty.squeeze() if isinstance(nifty, pd.DataFrame) else nifty
            fig_trend.add_trace(go.Scatter(x=nifty_index.index, y=nifty_series, mode='lines', name='Nifty 50', 
                                           line=dict(color='#888888', width=2, dash='dot', shape='spline')))
            
            fig_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color="#fafafa"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color="#fafafa"),
                hovermode="x unified", margin=dict(t=20, b=40, l=0, r=0), font=dict(color="#fafafa")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load historical data. Error: {e}")

# --- TAB 3: RISK ANALYTICS ---
with tab3:
    st.subheader("Quantitative Risk Metrics")
    st.markdown("Automated CAPM and Risk Profile calculation using 6-month daily variances.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        df_returns = pd.DataFrame({
            'Portfolio': hist_prices.pct_change().mean(axis=1),
            'Nifty': nifty.pct_change().squeeze()
        }).dropna()
        
        ann_volatility = df_returns['Portfolio'].std() * np.sqrt(252) * 100
        cov_matrix = np.cov(df_returns['Portfolio'], df_returns['Nifty'])
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        
        risk_free_rate = 0.07
        ann_return = df_returns['Portfolio'].mean() * 252
        sharpe_ratio = (ann_return - risk_free_rate) / (ann_volatility / 100)
        
        r1, r2, r3 = st.columns(3)
        r1.metric("Portfolio Beta (vs Nifty)", f"{beta:.2f}", delta="Low Volatility" if beta < 1 else "High Volatility", delta_color="inverse")
        r2.metric("Annualized Volatility", f"{ann_volatility:.2f}%")
        r3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}", help="Risk-adjusted return. > 1 is ideal.")
    except Exception as e:
        st.error("Waiting on historical data to calculate risk metrics...")

# --- TAB 4: STOCK SCREENER ---
with tab4:
    st.subheader("Deep-Dive Fundamental Screener")
    selected_stock = st.selectbox("Select a stock to generate an instant profile:", df_holdings['Ticker'].tolist())
    
    if selected_stock:
        st.write(f"#### Live Profile: {selected_stock} (NSE)")
        with st.spinner("Fetching secure data from Yahoo Finance..."):
            try:
                stock = yf.Ticker(f"{selected_stock}.NS")
                f_info = stock.fast_info
                
                pe = "Data Protected"
                div = "Data Protected"
                try:
                    deep_info = stock.info
                    if 'trailingPE' in deep_info: pe = f"{deep_info['trailingPE']:.2f}"
                    if 'dividendYield' in deep_info and deep_info['dividendYield'] is not None: div = f"{deep_info['dividendYield']*100:.2f}%"
                except: pass 
                
                mcap = getattr(f_info, 'market_cap', 0)
                high_52 = getattr(f_info, 'year_high', 0)
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("P/E Ratio", pe)
                c2.metric("Market Cap", f"₹{mcap / 10000000:,.0f} Cr" if mcap > 0 else "N/A")
                c3.metric("Dividend Yield", div)
                c4.metric("52 Week High", f"₹{high_52:,.2f}" if high_52 > 0 else "N/A")
                
                hist = stock.history(period="3mo")
                if not hist.empty:
                    fig_mini = px.area(hist, x=hist.index, y='Close', title=f"90-Day Price Action")
                    fig_mini.update_traces(line_color='#1c83e1', fillcolor='rgba(28, 131, 225, 0.2)')
                    fig_mini.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                        xaxis=dict(showgrid=False, color="#fafafa"), 
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color="#fafafa"), 
                        margin=dict(t=40, b=0, l=0, r=0), font=dict(color="#fafafa")
                    )
                    st.plotly_chart(fig_mini, use_container_width=True)
                    
            except Exception as e:
                st.warning("Yahoo Finance is currently restricting data access. Please try again later.")
