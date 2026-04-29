import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="AUD Global Currency Tracker", layout="wide")
st.title("🇦🇺 AUD Currency Performance Screener")

# Categorized Currency Lists
regions = {
    "Asia & SE Asia": {
        "Chinese Yuan": "AUDCNY=X", "Indian Rupee": "AUDINR=X", "Indonesian Rupiah": "AUDIDR=X",
        "Japanese Yen": "AUDJPY=X", "Malaysian Ringgit": "AUDMYR=X", "Philippine Peso": "AUDPHP=X",
        "Singapore Dollar": "AUDSGD=X", "South Korean Won": "AUDKRW=X", "Thai Baht": "AUDTHB=X",
        "Vietnamese Dong": "AUDVND=X", "Taiwan Dollar": "AUDTWD=X", "Hong Kong Dollar": "AUDHKD=X",
        "Pakistani Rupee": "AUDPKR=X", "Sri Lankan Rupee": "AUDLKR=X", "Bangladeshi Taka": "AUDBDT=X"
    },
    "Eastern Europe & Caucasus": {
        "Georgian Lari": "AUDGEL=X", "Czech Koruna": "AUDCZK=X", "Hungarian Forint": "AUDHUF=X",
        "Polish Zloty": "AUDPLN=X", "Romanian Leu": "AUDRON=X", "Turkish Lira": "AUDTRY=X",
        "Ukrainian Hryvnia": "AUDUAH=X", "Bulgarian Lev": "AUDBGN=X", "Serbian Dinar": "AUDRSD=X",
        "Armenian Dram": "AUDAMD=X", "Azerbaijani Manat": "AUDAZN=X", "Kazakhstani Tenge": "AUDKZT=X"
    },
    "South & Central America": {
        "Argentine Peso": "AUDARS=X", "Brazilian Real": "AUDBRL=X", "Chilean Peso": "AUDCLP=X", 
        "Colombian Peso": "AUDCOP=X", "Peruvian Sol": "AUDPEN=X", "Mexican Peso": "AUDMXN=X",
        "Uruguayan Peso": "AUDUYU=X", "Paraguayan Guarani": "AUDPYG=X", "Costa Rican Colon": "AUDCRC=X",
        "Guatemalan Quetzal": "AUDGTQ=X", "Honduran Lempira": "AUDHNL=X", "Nicaraguan Cordoba": "AUDNIO=X"
    }
}

@st.cache_data(ttl=86400)
def fetch_data(ticker):
    try:
        data = yf.download(ticker, period="1y", multi_level_index=False)
        if data.empty or len(data) < 2: return None
        
        start_price = float(data['Close'].iloc[0])
        end_price = float(data['Close'].iloc[-1])
        
        # % AUD rose = % Foreign Currency fell relative to AUD
        return ((end_price - start_price) / start_price) * 100
    except:
        return None

# Sidebar logic to process all data first
st.sidebar.header("Processing Data...")
all_results = []
for region_name, tickers in regions.items():
    for name, ticker in tickers.items():
        change = fetch_data(ticker)
        if change is not None:
            all_results.append({"Region": region_name, "Country": name, "AUD Change %": change})

full_df = pd.DataFrame(all_results)

# Create Tabs
tab_summary, tab_asia, tab_europe, tab_america = st.tabs([
    "🚨 Big Falls (>20%)", "Asia & SE Asia", "Eastern Europe", "South & Central America"
])

with tab_summary:
    st.subheader("Currencies that fell >20% against AUD in 1 Year")
    big_falls = full_df[full_df["AUD Change %"] > 20].sort_values("AUD Change %", ascending=False)
    if not big_falls.empty:
        st.table(big_falls[["Country", "Region", "AUD Change %"]].style.format({"AUD Change %": "{:.2f}%"}))
    else:
        st.info("No currencies fell by more than 20% in the selected period.")

def render_region_tab(tab_obj, region_name):
    with tab_obj:
        st.subheader(f"AUD Performance in {region_name}")
        region_df = full_df[full_df["Region"] == region_name].sort_values("AUD Change %", ascending=False)
        st.dataframe(region_df[["Country", "AUD Change %"]].style.format({"AUD Change %": "{:.2f}%"}), use_container_width=True)

render_region_tab(tab_asia, "Asia & SE Asia")
render_region_tab(tab_europe, "Eastern Europe & Caucasus")
render_region_tab(tab_america, "South & Central America")
