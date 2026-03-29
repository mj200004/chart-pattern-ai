
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import sys

sys.path.insert(0, ".")

st.set_page_config(
    page_title="Chart Pattern Intelligence | ET AI Hackathon",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background-color: #0D1117; }
  .stApp { background-color: #0D1117; color: #E6EDF3; }
  .signal-card { background: #161B22; border-radius: 10px; padding: 16px;
                 border-left: 4px solid #388BFD; margin-bottom: 12px; }
  .bullish { border-left-color: #3FB950 !important; }
  .bearish { border-left-color: #F85149 !important; }
  .metric-box { background: #161B22; border-radius: 8px;
                padding: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path("ps6_data")

# ── Data loaders ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(symbol: str) -> pd.DataFrame:
    safe = symbol.replace(".", "_")
    path = BASE_DIR / "ohlcv" / f"{safe}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)

@st.cache_data(ttl=300)
def load_detections() -> pd.DataFrame:
    path = BASE_DIR / "all_detections.parquet"
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()

@st.cache_data(ttl=300)
def load_daily_signals() -> list:
    path = BASE_DIR / "daily_signals.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def get_available_stocks() -> list:
    ohlcv_dir = BASE_DIR / "ohlcv"
    if not ohlcv_dir.exists():
        return ["RELIANCE.NS"]
    return sorted([f.stem.replace("_NS",".NS").replace("_",".") + ""
                   for f in ohlcv_dir.glob("*.parquet")])

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Chart Pattern Intelligence")
st.sidebar.caption("ET AI Hackathon 2026 | PS6")
page = st.sidebar.radio("Navigation",
    ["Daily Digest", "Stock Analysis", "Pattern Database", "About"])

# ── PAGE: Daily Digest ────────────────────────────────────────────────────────
if page == "Daily Digest":
    st.title("Today's Top Signals")
    st.caption("High-confidence patterns detected today across NSE 500 — with AI-generated signals")

    daily = load_daily_signals()
    if not daily:
        st.info("Run Notebooks 1-3 to generate signals. Sample data shown below.")
        daily = [
            {"symbol": "RELIANCE.NS", "pattern": "bullish_breakout",
             "signal": "BULLISH", "headline": "Reliance breaks 52-week resistance with strong volume",
             "explanation": "Stock broke above key resistance of Rs 1,420 with 2.3x average volume. Pattern has 72% historical win rate over 5 days on this stock.",
             "entry_note": "Enter above Rs 1,425 with volume confirmation",
             "stop_loss_note": "Stop below Rs 1,390 (below breakout candle)",
             "risk_reward": "1:2.5", "confidence": "HIGH",
             "confidence_score": 78, "current_price": 1422.5},
            {"symbol": "HDFCBANK.NS", "pattern": "double_bottom",
             "signal": "BULLISH", "headline": "HDFC Bank double bottom suggests strong reversal ahead",
             "explanation": "Two bottoms at Rs 1,520 zone with bounce. Classic bullish reversal pattern after 15% correction.",
             "entry_note": "Enter on close above Rs 1,560 neckline",
             "stop_loss_note": "Stop below Rs 1,510 (below second bottom)",
             "risk_reward": "1:3", "confidence": "HIGH",
             "confidence_score": 82, "current_price": 1545.0},
            {"symbol": "INFY.NS", "pattern": "head_and_shoulders",
             "signal": "BEARISH", "headline": "Infosys head and shoulders warns of near-term weakness",
             "explanation": "Classic topping pattern with head at Rs 1,890. Neckline at Rs 1,820 is the critical level to watch.",
             "entry_note": "Short entry on break below Rs 1,820 neckline",
             "stop_loss_note": "Stop above Rs 1,870 (above right shoulder)",
             "risk_reward": "1:2", "confidence": "MEDIUM",
             "confidence_score": 65, "current_price": 1835.0},
        ]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    bullish = sum(1 for s in daily if s.get("signal") == "BULLISH")
    bearish = sum(1 for s in daily if s.get("signal") == "BEARISH")
    high_conf = sum(1 for s in daily if s.get("confidence") == "HIGH")
    col1.metric("Total Signals", len(daily))
    col2.metric("Bullish", bullish, delta=f"+{bullish}")
    col3.metric("Bearish", bearish, delta=f"-{bearish}", delta_color="inverse")
    col4.metric("High Confidence", high_conf)

    st.divider()

    for sig in daily:
        direction = sig.get("signal", "NEUTRAL")
        css_class = "bullish" if direction == "BULLISH" else ("bearish" if direction == "BEARISH" else "")
        icon = "▲" if direction == "BULLISH" else ("▼" if direction == "BEARISH" else "~")
        color = "#3FB950" if direction == "BULLISH" else ("#F85149" if direction == "BEARISH" else "#8B949E")

        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"#### {sig.get('symbol','')}  {icon} {sig.get('headline','')}")
                st.caption(f"Pattern: `{sig.get('pattern','')}` | Confidence score: {sig.get('confidence_score', 0):.0f}%")
                st.write(sig.get("explanation", ""))
                ec1, ec2, ec3 = st.columns(3)
                ec1.info(f"**Entry:** {sig.get('entry_note', 'N/A')}")
                ec2.error(f"**Stop loss:** {sig.get('stop_loss_note', 'N/A')}")
                ec3.success(f"**R:R:** {sig.get('risk_reward', 'N/A')}")
            with c2:
                st.metric("Current price",
                         f"Rs {sig.get('current_price', 0):,.2f}")
                st.markdown(f"<span style='color:{color};font-weight:bold;font-size:18px'>{direction}</span>",
                           unsafe_allow_html=True)
            st.divider()

# ── PAGE: Stock Analysis ─────────────────────────────────────────────────────
elif page == "Stock Analysis":
    st.title("Stock Pattern Analysis")
    available = get_available_stocks()
    selected = st.selectbox("Select stock", available if available else ["RELIANCE.NS"])
    lookback = st.slider("Chart lookback (days)", 60, 365, 180)

    df = load_stock_data(selected)
    if df.empty:
        st.warning("No data. Run Notebook 1 first.")
        st.stop()

    df_plot = df.tail(lookback).copy()

    # Build Plotly candlestick
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.02)

    fig.add_trace(go.Candlestick(
        x=df_plot.index, open=df_plot['open'], high=df_plot['high'],
        low=df_plot['low'], close=df_plot['close'],
        increasing_line_color='#3FB950', decreasing_line_color='#F85149',
        name='Price'
    ), row=1, col=1)

    if 'ma20' in df_plot.columns:
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ma20'],
            line=dict(color='#F78166', width=1), name='MA20'), row=1, col=1)
    if 'ma50' in df_plot.columns:
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['ma50'],
            line=dict(color='#FFA657', width=1), name='MA50'), row=1, col=1)

    # Volume bars
    colors = ['#3FB950' if r >= 0 else '#F85149'
              for r in df_plot['returns'].fillna(0)]
    fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['volume'],
        marker_color=colors, name='Volume', opacity=0.7), row=2, col=1)

    fig.update_layout(
        title=f'{selected} — Interactive Chart',
        plot_bgcolor='#161B22', paper_bgcolor='#0D1117',
        font=dict(color='#E6EDF3'),
        xaxis_rangeslider_visible=False,
        height=600, showlegend=True,
        legend=dict(bgcolor='#161B22', bordercolor='#30363D')
    )
    fig.update_xaxes(gridcolor='#21262D', showgrid=True)
    fig.update_yaxes(gridcolor='#21262D', showgrid=True)

    st.plotly_chart(fig, use_container_width=True)

    # Show detections for this stock
    df_det = load_detections()
    if not df_det.empty:
        stock_det = df_det[df_det['symbol'] == selected]
        if not stock_det.empty:
            st.subheader(f"Patterns detected in {selected}")
            display_cols = ['pattern', 'confidence', 'start_date', 'end_date']
            show_cols = [c for c in display_cols if c in stock_det.columns]
            st.dataframe(stock_det[show_cols].sort_values('confidence', ascending=False),
                        use_container_width=True)

# ── PAGE: Pattern Database ────────────────────────────────────────────────────
elif page == "Pattern Database":
    st.title("Pattern Detection Database")
    df_det = load_detections()
    if df_det.empty:
        st.info("No detections yet. Run Notebooks 1 and 2 first.")
    else:
        # Filters
        patterns = ['All'] + sorted(df_det['pattern'].unique().tolist())
        sel_pattern = st.selectbox("Filter by pattern", patterns)
        min_conf = st.slider("Min confidence", 0.0, 1.0, 0.5)
        filtered = df_det.copy()
        if sel_pattern != 'All':
            filtered = filtered[filtered['pattern'] == sel_pattern]
        filtered = filtered[filtered['confidence'] >= min_conf]
        st.dataframe(filtered.sort_values('confidence', ascending=False),
                    use_container_width=True)
        st.caption(f"Showing {len(filtered)} detections")

# ── PAGE: About ──────────────────────────────────────────────────────────────
elif page == "About":
    st.title("About this Project")
    st.markdown("""
    ## Chart Pattern Intelligence
    **ET AI Hackathon 2026 | PS6 — AI for the Indian Investor**

    ### What it does
    Automatically detects classic chart patterns across NSE/BSE stocks using
    computer vision and pattern recognition, then generates actionable
    plain-English signals using Claude (Anthropic).

    ### Tech stack
    - **Data**: yfinance, nsepy, Pandas, Parquet
    - **Pattern detection**: OpenCV, SciPy, PyTorch (ResNet-18), scikit-learn
    - **AI signals**: Anthropic Claude claude-sonnet-4-20250514 API
    - **Dashboard**: Streamlit + Plotly

    ### Patterns detected
    Head & Shoulders, Double Top, Double Bottom, Bullish/Bearish Breakout,
    Support/Resistance Zones, Bull Flag, Bear Flag

    ### How to run
    ```bash
    # 1. Set API key
    export ANTHROPIC_API_KEY=your-key
    # 2. Run data pipeline
    jupyter nbconvert --to notebook --execute nb1_data_ingestion.ipynb
    jupyter nbconvert --to notebook --execute nb2_pattern_detection.ipynb
    jupyter nbconvert --to notebook --execute nb3_backtester_claude.ipynb
    # 3. Launch dashboard
    streamlit run app.py
    ```
    """)
