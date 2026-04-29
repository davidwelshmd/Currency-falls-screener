import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="AUD Global Currency Tracker", layout="wide")

# --- APP STYLING & TITLE ---
st.title("🇦🇺 AUD Global Currency Performance Screener")
st.write("Checking AUD strength against global regions over a 1-year lookback.")

# --- COMPREHENSIVE REGIONAL MAPPING ---
regions = {
    "Asia & SE Asia": {
        "Chinese Yuan": "AUDCNY=X", "Indian Rupee": "AUDINR=X", "Indonesian Rupiah": "AUDIDR=X",
        "Japanese Yen": "AUDJPY=X", "Malaysian Ringgit": "AUDMYR=X", "Philippine Peso": "AUDPHP=X",
        "Singapore Dollar": "AUDSGD=X", "South Korean Won": "AUDKRW=X", "Thai Baht": "AUDTHB=X",
        "Vietnamese Dong": "AUDVND=X", "Taiwan Dollar": "AUDTWD=X", "Hong Kong Dollar": "AUDHKD=X",
        "Pakistani Rupee": "AUDPKR=X", "Sri Lankan Rupee": "AUDLKR=X", "Bangladeshi Taka": "AUDBDT=X",
        "Mongolian Tugrik": "AUDMNT=X"
    },
    "Europe, Russia & Caucasus": {
        "Russian Ruble": "AUDRUB=X", 
        "Euro (Estonia, Latvia, Lithuania, etc.)": "AUDEUR=X",
        "Georgian Lari": "AUDGEL=X", "Czech Koruna": "AUDCZK=X", "Hungarian Forint": "AUDHUF=X",
        "Polish Zloty": "AUDPLN=X", "Romanian Leu": "AUDRON=X", "Turkish Lira": "AUDTRY=X",
        "Ukrainian Hryvnia": "AUDUAH=X", "Bulgarian Lev": "AUDBGN=X", "Serbian Dinar": "AUDRSD=X",
        "Armenian Dram": "AUDAMD=X", "Azerbaijani Manat": "AUDAZN=X"
    },
    "Middle East & Central Asia": {
        "Iranian Rial": "AUDIRR=X", "Israeli Shekel": "AUDILS=X", "Jordanian Dinar": "AUDJOD=X",
        "Saudi Riyal": "AUDSAR=X", "UAE Dirham": "AUDAED=X", "Qatari Riyal": "AUDQAR=X",
        "Kuwaiti Dinar": "AUDKWD=X", "Omani Rial": "AUDOMR=X", "Kazakhstani Tenge": "AUDKZT=X",
        "Uzbekistani Som": "AUDUZS=X"
    },
    "South & Central America": {
        "Argentine Peso": "AUDARS=X", "Brazilian Real": "AUDBRL=X", "Chilean Peso": "AUDCLP=X", 
        "Colombian Peso": "AUDCOP=X", "Peruvian Sol": "AUDPEN=X", "Mexican Peso": "AUDMXN=X",
        "Uruguayan Peso": "AUDUYU=X", "Paraguayan Guarani": "AUDPYG=X", "Costa Rican Colon": "AUDCRC=X",
        "Guatemalan Quetzal": "AUDGTQ=X"
    }
}

# --- DATA FETCHING FUNCTION ---
@st.cache_data(ttl=86400)
def fetch_currency_data(ticker):
    try:
        # Fetch 1 year of data
        data = yf.download(ticker, period="1y", multi_level_index=False)
        if data.empty or len(data) < 2:
            return None
        
        start_val = float(data['Close'].iloc[0])
        end_val = float(data['Close'].iloc[-1])
        
        if start_val == 0: return None
        
        # % AUD gain = % Foreign Currency fall
        pct_change = ((end_val - start_val) / start_val) * 100
        return pct_change
    except:
        return None

# --- SIDEBAR & PROCESSING ---
st.sidebar.header("Settings")
exclude_hyper = st.sidebar.checkbox("Cap display at 100% gain", value=False, help="Hides extreme outliers like the Iranian Rial for better table reading.")

# Progress indicator
all_results = []
progress_text = "Fetching global exchange rates..."
my_bar = st.progress(0, text=progress_text)

total_tickers = sum(len(v) for v in regions.values())
counter = 0

for region_name, tickers in regions.items():
    for country_name, ticker in tickers.items():
        counter += 1
        change = fetch_currency_data(ticker)
        if change is not None:
            all_results.append({
                "Region": region_name,
                "Country/Currency": country_name,
                "AUD Change %": change
            })
        my_bar.progress(counter / total_tickers)

my_bar.empty()
full_df = pd.DataFrame(all_results)

# --- TABS LAYOUT ---
tab_alert, tab_asia, tab_europe, tab_mideast, tab_latam = st.tabs([
    "🚨 Big Falls (>20%)", "Asia & SE Asia", "Europe & Russia", "Middle East", "Americas"
])

# 1. ALERT TAB
with tab_alert:
    st.subheader("Currencies that fell >20% against AUD (1 Year)")
    # Filter for >20%
    big_falls = full_df[full_df["AUD Change %"] > 20].sort_values("AUD Change %", ascending=False)
    
    if exclude_hyper:
        display_falls = big_falls[big_falls["AUD Change %"] <= 100]
    else:
        display_falls = big_falls

    if not display_falls.empty:
        st.dataframe(
            display_falls.style.format({"AUD Change %": "{:.2f}%"}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No currencies fell by more than 20% in the selected period.")

# HELPER FUNCTION FOR REGIONAL TABS
def show_region(tab_name, region_key):
    with tab_name:
        st.subheader(f"AUD vs {region_key}")
        rdf = full_df[full_df["Region"] == region_key].sort_values("AUD Change %", ascending=False)
        st.dataframe(
            rdf[["Country/Currency", "AUD Change %"]].style.format({"AUD Change %": "{:.2f}%"}),
            use_container_width=True,
            hide_index=True
        )

# 2. REGIONAL TABS
show_region(tab_asia, "Asia & SE Asia")
show_region(tab_europe, "Europe, Russia & Caucasus")
show_region(tab_mideast, "Middle East & Central Asia")
show_region(tab_latam, "South & Central America")

st.divider()
st.caption(f"Data sourced from Yahoo Finance. Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
