import pandas as pd
import numpy as np
import yfinance as yf
import os

# Mapping user-friendly names to Yahoo tickers
INDIAN_TICKER_MAP = {
    "RELIANCE": "RELIANCE.NS",
    "RIL": "RELIANCE.NS",

    "HDFC": "HDFC.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "HDFC BANK": "HDFCBANK.NS",

    "ICICI": "ICICIBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",

    "AXIS": "AXISBANK.NS",
    "AXIS BANK": "AXISBANK.NS",
    "AXISBANK": "AXISBANK.NS",

    "TCS": "TCS.NS",
    "TATA CONSULTANCY": "TCS.NS",


    "INFY": "INFY.NS",
    "INFOSYS": "INFY.NS",
    "INFOSYS LTD": "INFY.NS",
    "INFOSYS LIMITED": "INFY.NS",


    "WIPRO": "WIPRO.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "MARUTI": "MARUTI.NS",
    "ITC": "ITC.NS",
    "HUL": "HINDUNILVR.NS",

    "SBIN": "SBIN.NS",
    "SBI": "SBIN.NS",
    "STATE BANK": "SBIN.NS"
}

class DataAgent:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        if os.path.exists(csv_path):
            self.data = pd.read_csv(csv_path, parse_dates=["Date"])
        else:
            print("CSV not found. Creating empty dataset.")
            self.data = pd.DataFrame(columns=["Date","Ticker","Open","High","Low","Close","Volume"])

    # Normalize user-input ticker
    def normalize_ticker(self, user_input):
        s = user_input.strip().upper()
        if s in INDIAN_TICKER_MAP:
            return INDIAN_TICKER_MAP[s]
        return s if s.endswith(".NS") else s + ".NS"

    # Fetch data from Yahoo Finance
    def _fetch_from_yahoo(self, ticker, start_date, end_date):
        print(f"Fetching {ticker} from Yahoo Finance...")
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                print("Yahoo returned empty.")
                return pd.DataFrame()
            df = df.reset_index()
            df["Ticker"] = ticker
            return df[["Date","Ticker","Open","High","Low","Close","Volume"]]
        except Exception as e:
            print("Yahoo error:", e)
            return pd.DataFrame()

    # Main: load CSV + fallback
    def get_data(self, user_ticker, start_date, end_date):
        ticker = self.normalize_ticker(user_ticker)
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        df = self.data.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dropna()

        df_ticker = df[df["Ticker"] == ticker]

        need_download = False
        fetch_start = start_date
        fetch_end = end_date

        if df_ticker.empty:
            need_download = True
        else:
            csv_min = df_ticker["Date"].min()
            csv_max = df_ticker["Date"].max()

            if start_date < csv_min or end_date > csv_max:
                need_download = True
                fetch_start = min(start_date, csv_min)
                fetch_end   = max(end_date, csv_max)

        if need_download:
            yahoo_df = self._fetch_from_yahoo(ticker, fetch_start, fetch_end)
            if not yahoo_df.empty:
                df = pd.concat([df, yahoo_df], ignore_index=True)
                df = df.drop_duplicates(["Date","Ticker"])
                df = df.sort_values(["Ticker","Date"])
                df.to_csv(self.csv_path, index=False)
                self.data = df

        df_final = df[(df["Ticker"] == ticker) &
                      (df["Date"] >= start_date) &
                      (df["Date"] <= end_date)]

        if df_final.empty:
            raise ValueError(f"No data found for {ticker} after fallback.")

        return df_final.reset_index(drop=True)

    # Indicators
    def compute_indicators(self, df):

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss

        df["RSI"] = 100 - (100 / (1 + rs))

        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()

        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        sma20 = df["Close"].rolling(20).mean()
        std20 = df["Close"].rolling(20).std()

        df["BB_upper"] = sma20 + 2 * std20
        df["BB_lower"] = sma20 - 2 * std20

        return df

    # Summary
    def get_indicator_summary(self, df):
        latest = df.iloc[-1]
        return {
            "RSI": float(latest["RSI"]),
            "MACD": float(latest["MACD"]),
            "Signal": float(latest["Signal"]),
            "BB_upper": float(latest["BB_upper"]),
            "BB_lower": float(latest["BB_lower"]),
            "Close": float(latest["Close"]),
            "Date": str(latest["Date"]),
        }
