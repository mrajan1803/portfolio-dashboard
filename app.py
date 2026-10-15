import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="₹1 Cr Equity Portfolio", page_icon="📈", layout="wide")

# 2. Header
st.title("📈 ₹1 Crore Advanced Equity Portfolio Dashboard")
st.markdown("Interactive analytics for Sector Allocation, Market Cap, and Performance Tracking.")

# 3. Fetch Live Data
sheet_csv_url = "https://docs.google.com/spreadsheets/d/1OzqcT2AWsknaZceIe06ph0yn904YDp7BViqEErgCGEw/export?format=csv&gid=1991889713"

@st.cache_data(ttl=300) # Caches data for 5 mins so it's fast but stays fresh
def load_data():
    df = pd.read_csv(sheet_csv_url)
    df = df.dropna(subset=['Ticker'])
    
    # Clean numeric columns
    numeric_cols = ['Shares Held', 'Average Buy Price (INR)', 'Target Weight (%)', 
                    'Current Price (INR)', 'Market Value (INR)', 'Invested Cost (INR)', 'Unrealized P/L (INR)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[₹,%]', '', regex=True), errors='coerce').fillna(0)
    
    # Add Return Percentage
    df['Net Return (%)'] = (df['Unrealized P/L (INR)'] / df['Invested Cost (INR)']) * 100
    df['Net Return (%)'] = df['Net Return (%)'].fillna(0)
    
    # Add Advanced Portfolio Meta-Data (from your Fundamentals)
    meta_data = {
        'HDFCBANK': {'Sector': 'Financials', 'Cap': 'Large Cap', 'Score': 85.0},
        'ICICIBANK': {'Sector': 'Financials', 'Cap': 'Large Cap', 'Score': 86.5},
        'RELIANCE': {'Sector': 'Conglomerate', 'Cap': 'Large Cap', 'Score': 78.2},
        'BHARTIARTL': {'Sector': 'Telecom', 'Cap': 'Large Cap', 'Score': 79.8},
        'LT': {'Sector': 'Infrastructure', 'Cap': 'Large Cap', 'Score': 81.1},
        'SUNPHARMA': {'Sector': 'Pharma', 'Cap': 'Large Cap', 'Score': 80.5},
        'TCS': {'Sector': 'IT', 'Cap': 'Large Cap', 'Score': 82.3},
        'HCLTECH': {'Sector': 'IT', 'Cap': 'Large Cap', 'Score': 81.8},
        'NTPC': {'Sector': 'Energy', 'Cap': 'Large Cap', 'Score': 77.5},
        'HINDUNILVR': {'Sector': 'FMCG', 'Cap': 'Large Cap', 'Score': 75.0},
        'MRF': {'Sector': 'Auto', 'Cap': 'Large Cap', 'Score': 76.5},
        'OBEROIRLTY': {'Sector': 'Realty', 'Cap': 'Mid Cap', 'Score': 79.5},
        'MPHASIS': {'Sector': 'IT', 'Cap': 'Mid Cap', 'Score': 78.8},
        'REDINGTON': {'Sector': 'IT', 'Cap': 'Small Cap', 'Score': 77.2},
        'ECLERX': {'Sector': 'IT', 'Cap': 'Small Cap', 'Score': 79.1}
    }
    
    df['Sector'] = df['Ticker'].apply(lambda x: meta_data.get(x, {}).get('Sector', 'Other'))
    df['Market Cap'] = df['Ticker'].apply(lambda x: meta_data.get(x, {}).get('Cap', 'Other'))
    df['Composite Score'] = df['Ticker'].apply(lambda x: meta_data.get(x, {}).get('Score', 0))
    
    return df

try:
    df_holdings = load_data()
except Exception as e:
    st.error("Failed to load data. Please ensure your Google Sheet link is correct and publicly viewable.")
    st.stop()

# 4. Top Level KPIs
total_invested = df_holdings['Invested Cost (INR)'].sum()
total_value = df_holdings['Market Value (INR)'].sum()
total_pnl = df_holdings['Unrealized P/L (INR)'].sum()
overall_return = (total_pnl / total_invested) * 100 if total_invested > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Invested Cost", f"₹{total_invested:,.0f}")
kpi2.metric("Current Market Value", f"₹{total_value:,.0f}", delta=f"₹{total_pnl:,.0f}")
kpi3.metric("Unrealized P&L", f"₹{total_pnl:,.0f}")
kpi4.metric("Overall Net Return", f"{overall_return:.2f}%")

st.divider()

# 5. Create TABS for Better Organization
tab1, tab2, tab3 = st.tabs(["📊 Allocation & Holdings", "📈 Analytics & Performance", "🏆 Top Performers"])

# --- TAB 1: ALLOCATION & HOLDINGS ---
with tab1:
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        fig_sector = px.pie(df_holdings, values='Market Value (INR)', names='Sector', 
                            title='Exposure by Sector', hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
        fig_sector.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sector, use_container_width=True)
        
    with col_pie2:
        fig_cap = px.pie(df_holdings, values='Market Value (INR)', names='Market Cap', 
                         title='Exposure by Market Cap Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_cap.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cap, use_container_width=True)
    
    st.subheader("Live Portfolio Tracker")
    display_df = df_holdings[['Ticker', 'Company Name', 'Sector', 'Market Cap', 'Shares Held', 
                              'Average Buy Price (INR)', 'Current Price (INR)', 'Market Value (INR)', 
                              'Unrealized P/L (INR)', 'Net Return (%)']]
    
    # Beautiful formatting for the dataframe
    st.dataframe(
        display_df.style.format({
            'Average Buy Price (INR)': '₹{:,.2f}',
            'Current Price (INR)': '₹{:,.2f}',
            'Market Value (INR)': '₹{:,.0f}',
            'Unrealized P/L (INR)': '₹{:,.0f}',
            'Net Return (%)': '{:.2f}%'
        }).map(lambda val: 'color: #00C851' if val > 0 else 'color: #ff4444', subset=['Unrealized P/L (INR)', 'Net Return (%)']),
        use_container_width=True, hide_index=True
    )


# --- TAB 2: ANALYTICS & PERFORMANCE ---
with tab2:
    st.subheader("Invested Cost vs. Current Market Value")
    # Grouped Bar Chart
    df_sorted = df_holdings.sort_values(by='Invested Cost (INR)', ascending=False)
    fig_compare = go.Figure(data=[
        go.Bar(name='Invested Cost', x=df_sorted['Ticker'], y=df_sorted['Invested Cost (INR)'], marker_color='#17365D'),
        go.Bar(name='Current Value', x=df_sorted['Ticker'], y=df_sorted['Market Value (INR)'], marker_color='#4285F4')
    ])
    fig_compare.update_layout(barmode='group', xaxis_title="Stock", yaxis_title="Value (INR)", hovermode="x unified")
    st.plotly_chart(fig_compare, use_container_width=True)

    st.divider()

    st.subheader("Fundamental Composite Scores")
    # Score Bar Chart
    df_scores = df_holdings.sort_values(by='Composite Score', ascending=True)
    fig_score = px.bar(df_scores, x='Composite Score', y='Ticker', orientation='h', 
                       title='Stock Quality Ranking (0-100)', color='Composite Score', color_continuous_scale='Blues')
    st.plotly_chart(fig_score, use_container_width=True)


# --- TAB 3: TOP PERFORMERS ---
with tab3:
    st.subheader("Top Gainers & Losers (Overall Return %)")
    
    df_perf = df_holdings.sort_values(by='Net Return (%)', ascending=False)
    gainers = df_perf.head(5)
    losers = df_perf.tail(5).sort_values(by='Net Return (%)', ascending=True)
    
    col_gainer, col_loser = st.columns(2)
    
    with col_gainer:
        st.success("🟢 Top 5 Gainers")
        st.dataframe(gainers[['Ticker', 'Company Name', 'Net Return (%)', 'Unrealized P/L (INR)']].style.format({
            'Net Return (%)': '+{:.2f}%',
            'Unrealized P/L (INR)': '₹{:,.0f}'
        }), use_container_width=True, hide_index=True)
        
    with col_loser:
        st.error("🔴 Top 5 Losers")
        st.dataframe(losers[['Ticker', 'Company Name', 'Net Return (%)', 'Unrealized P/L (INR)']].style.format({
            'Net Return (%)': '{:.2f}%',
            'Unrealized P/L (INR)': '₹{:,.0f}'
        }), use_container_width=True, hide_index=True)
        
    st.info("💡 Note: Return percentage is calculated based on current market prices compared to your simulated reference buy prices.")
