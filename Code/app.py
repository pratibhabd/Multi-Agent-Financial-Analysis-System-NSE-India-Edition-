# app.py
import pandas as pd
import streamlit as st
from agents import run_financial_agents


import streamlit as st

st.markdown("""
<style>

    /* ===== Sidebar background ===== */
    [data-testid="stSidebar"] {
        background-color: #D8BFD8 !important;   /* Light sidebar color */
    }

    /* ===== Main page background ===== */
    [data-testid="stAppViewContainer"] {
        background-color: #f5f9ff!important;  /* Soft background */
    }

    /* ===== Top bar (Deploy/Settings bar) ===== */
    [data-testid="stHeader"] {
        background-color: #f5f9ff !important;  /* Match main page */
        color: black !important;
    }

    /* Remove shadow under the top header */
    header[data-testid="stHeader"] {
        box-shadow: none !important;
    }

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

    /* Sidebar Light Purple */
    [data-testid="stSidebar"] {
        background-color: #F3E8FF !important;
    }

    /* Main Page Background Image */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1605902711622-cfb43c44367e?w=1200&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Soft top navigation bar */
    [data-testid="stHeader"] {
        background-color: rgba(255,255,255,0.6) !important;
        backdrop-filter: blur(8px);
    }

</style>
""", unsafe_allow_html=True)



def flatten_chart_paths(chart_dict):
    """
    Recursively flatten chart paths dictionary into a list of file paths
    """
    paths = []
    for value in chart_dict.values():
        if isinstance(value, dict):
            paths.extend(flatten_chart_paths(value))
        else:
            paths.append(value)
    return paths

st.set_page_config(page_title="Financial Analysis Dashboard", layout="wide")

st.title("Multi-Agent Financial Analysis System")

# ------------------------------
# 1️ Sidebar Inputs
# ------------------------------
st.sidebar.header("Input Parameters")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
# ------------------------------
# 2️ Run Analysis Button
# ------------------------------
if st.sidebar.button("Run Analysis"):

    if ticker and start_date and end_date:
        with st.spinner(f"Running financial analysis for {ticker}..."):

            try:
                result= run_financial_agents(ticker, start_date, end_date)
                st.success(f"Analysis completed!")

                st.subheader(f"Summary for {ticker} Stock from {start_date} to {end_date}")
                st.write(result["summary"])# this will display the full string from llm

                #st.subheader("News Articles")
                #st.write(result["articles"])

                st.subheader("Graphs Summary")

                # Display charts
                charts = result["charts"]
                for path in flatten_chart_paths(charts):
                    st.image(path)

                # Display PDF download link
                with open(result["pdf_path"], "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{ticker}_financial_report.pdf",
                    mime="application/pdf",
                    key=f"{ticker}_pdf_download"
                )

            except Exception as e:
                st.error(f"Error running workflow: {e}")
    else:
        st.warning("Please provide all input parameters!")

# ------------------------------
# 3️ Optional: Display Instructions
# ------------------------------
st.markdown("""
### How it works:
1. Enter a stock ticker and date range.
2. Click "Run Analysis".
3. Wait for the multi-agent system to fetch data, run analysis, generate charts, and summarize results via LLM.
4. Download the PDF report.
""")
