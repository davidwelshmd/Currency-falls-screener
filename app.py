import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Title and description
st.title("🇦🇺 AUD Currency Performance Tracker")
st.write("Checking AUD against SA, Asia, SE Asia, and E. Europe (1 Year)")

# Define currency pairs (AUD vs others)
# Format: CURRENCY=X
pairs = {
    # South America
    "Argentine Peso": "ARS=X", "Brazilian Real": "BRL=X", "Chilean Peso": "CLP=X", 
    "Colombian Peso": "COP=X", "Peruvian Sol": "PEN=X",
    # Asia/SE Asia
    "Chinese Yuan": "CNY=X", "Indian Rupee": "INR=X", "Indonesian Rupiah": "IDR=X",
    "Japanese Yen": "JPY=X", "Malaysian Ringgit": "MYR=X", "Philippine Peso": "PHP=X",
    "Singapore Dollar": "SGD=X", "South Korean Won": "KRW=X", "Thai Baht": "THB=X",
    "Vietnamese Dong": "VND=X",
    # Eastern Europe
    "Czech Koruna": "CZK=X", "Hungarian Forint": "HUF=X", "Polish Zloty": "PLN=X",
    "Romanian Leu": "RON=X", "Turkish Lira": "TRY=X", "Ukrainian Hryvnia": "UAH=X"
}

@st.cache_data(ttl=86400) # Cache for 24 hours
def get_data(ticker):
    try:
        # Get historical data
        end = datetime.now()
        start = end - timedelta(days=365)
        data = yf.download(ticker, start=start, end=end)
        
        if len(data) < 2: return None
        
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        
        # Performance calculation (Higher means AUD strengthened)
        change = ((end_price - start_price) / start_price) * 100
        return change
    except Exception as e:
        return None

# Process data
results = []
for name, ticker in pairs.items():
    change = get_data(ticker)
    if change is not None:
        results.append({"Country/Currency": name, "AUD 1Y Change %": change})

df = pd.DataFrame(results)

# Filter for biggest falls (>20% fall in currency, i.e., >20% rise in AUD)
# We look for AUD strength, so positive change means AUD rose
filtered_df = df[df["AUD 1Y Change %"] > 20].sort_values(by="AUD 1Y Change %", ascending=False)

# Display Results
st.subheader("⚠️ Currencies that fell >20% against AUD (1 Year)")
if not filtered_df.empty:
    st.dataframe(filtered_df.style.format({"AUD 1Y Change %": "{:.2f}%"}))
else:
    st.success("No currencies fell by more than 20% over the last year.")

st.subheader("All Monitored Pairs")
st.dataframe(df.sort_values(by="AUD 1Y Change %", ascending=False))
