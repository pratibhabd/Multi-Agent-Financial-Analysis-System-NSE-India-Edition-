from DataAgent import DataAgent
from AnalysisAgent import AnalysisAgent
from NewsAgent import NewsAgent
from ReportAgent import ReportAgent
from VisualizationAgent import VisualizationAgent


if __name__ == "__main__":

    #1.DATA AGENT
    data_agent = DataAgent("master_investment_dataset.csv")

    # Inputs coming from user UI
    ticker = "RELIANCE.NS"
    start = "2024-01-01"
    end = "2025-03-31"

    df = data_agent.get_data(ticker, start, end)
    df = data_agent.compute_indicators(df)

    technical_summary = data_agent.get_indicator_summary(df)

    print(technical_summary)

    #2. ANALYSIS AGENT
    analysis_agent = AnalysisAgent(ticker="RELIANCE.NS")
    analysis_output = analysis_agent.run(df, technical_summary)

    print("\n===== FINAL ANALYSIS =====")
    print(analysis_output)

    #3. NEWS AGENT

    news_agent = NewsAgent(ticker="RELIANCE.NS")

    articles = news_agent.fetch_news(start_date="2024-01-01", end_date="2025-03-31")
    sentiment_summary = news_agent.summarize_sentiment(articles)

    print("Fetched News:", articles)
    print("Summary:", sentiment_summary)

    #for i in range(0,len(articles)):
        #print(f"Title{i} :{articles[i]["title"]}, Sentiment:{articles[i]['sentiment']}, Source:{articles[i]['link']}")

    # 4. VISUALIZATION AGENT

    viz_agent = VisualizationAgent(ticker="RELIANCE.NS")
    chart_paths = viz_agent(df, analysis_output,sentiment_summary)

    #5.REPORT AGENT
    charts_list = []
    for key, val in chart_paths.items():
        if isinstance(val, dict):  # e.g., indicators
            charts_list.extend(val.values())
        else:
            charts_list.append(val)

    final_analysis = {
        "ticker": ticker,
        "start":start,
        "end":end,
        "technical": technical_summary,
        "sentiment": sentiment_summary,
        "final_signal": analysis_output["signal"],
        "summary": analysis_output["indicator_explanations"]["MACD"],
        "charts":charts_list
    }
    report_agent = ReportAgent()
    report_file = report_agent.generate_report(
        analysis=final_analysis
    )
    print(f"\n Report generated successfully: {report_file}")



