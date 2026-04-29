import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Title and description
st.set_page_config(page_title="AUD Currency Screener", page_icon="🇦🇺")
st.title("🇦🇺 AUD Currency Performance Tracker")
st.write("Checking AUD against South America, Asia, SE Asia, and E. Europe (1 Year Lookback)")

# Define currency pairs (AUD vs others)
# yfinance uses 'AUDXXX=X' for AUD to Foreign Currency rates
pairs = {
    # South America
    "Argentine Peso": "AUDARS=X", "Brazilian Real": "AUDBRL=X", "Chilean Peso": "AUDCLP=X", 
    "Colombian Peso": "AUDCOP=X", "Peruvian Sol": "AUDPEN=X",
    # Asia/SE Asia
    "Chinese Yuan": "AUDCNY=X", "Indian Rupee": "AUDINR=X", "Indonesian Rupiah": "AUDIDR=X",
    "Japanese Yen": "AUDJPY=X", "Malaysian Ringgit": "AUDMYR=X", "Philippine Peso": "AUDPHP=X",
    "Singapore Dollar": "AUDSGD=X", "South Korean Won": "AUDKRW=X", "Thai Baht": "AUDTHB=X",
    "Vietnamese Dong": "AUDVND=X",
    # Eastern Europe
    "Czech Koruna": "AUDCZK=X", "Hungarian Forint": "AUDHUF=X", "Polish Zloty": "AUDPLN=X",
    "Romanian Leu": "AUDRON=X", "Turkish Lira": "AUDTRY=X", "Ukrainian Hryvnia": "AUDUAH=X"
}

@st.cache_data(ttl=86400) # Cache data for 24 hours
def get_currency_data(ticker):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # multi_level_index=False prevents the common ValueError in new yfinance versions
        data = yf.download(ticker, start=start_date, end=end_date, multi_level_index=False)
        
        if data.empty or len(data) < 2:
            return None
        
        # Get the first and last available 'Close' prices
        start_price = float(data['Close'].iloc[0])
        end_price = float(data['Close'].iloc[-1])
        
        if start_price == 0: return None
        
        # Calculation: How much the AUD rose against the currency
        # (Positive % means AUD strengthened / Foreign Currency fell)
        percent_change = ((end_price - start_price) / start_price) * 100
        return percent_change
    except Exception as e:
        return None

# Process data with a progress bar
results = []
progress_bar = st.progress(0)
status_text = st.empty()

for i, (name, ticker) in enumerate(pairs.items()):
    status_text.text(f"Fetching: {name} ({ticker})")
    change = get_currency_data(ticker)
    if change is not None:
        results.append({"Country/Currency": name, "AUD 1Y Change %": change})
    progress_bar.progress((i + 1) / len(pairs))

status_text.text("Analysis Complete!")
progress_bar.empty()

# Create DataFrame
df = pd.DataFrame(results)

# Filter for biggest falls (>20% rise in AUD value means >20% fall in that currency)
filtered_df = df[df["AUD 1Y Change %"] > 20].sort_values(by="AUD 1Y Change %", ascending=False)

# Display High-Impact Results
st.subheader("⚠️ Currencies that fell >20% against AUD (1 Year)")
if not filtered_df.empty:
    st.write("These countries are significantly cheaper for AUD holders than they were a year ago.")
    st.table(filtered_df.style.format({"AUD 1Y Change %": "{:.2f}%"}))
else:
    st.info("No monitored currencies fell by more than 20% over the last year.")

# Display All Data
with st.expander("View Full List (All Monitored Regions)"):
    st.dataframe(df.sort_values(by="AUD 1Y Change %", ascending=False), use_container_width=True)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
