# agents.py
import pandas as pd
from agno.agent import Agent
from agno.workflow import Workflow
from groq import Groq
import os
from dotenv import load_dotenv
from DataAgent import DataAgent
from AnalysisAgent import AnalysisAgent
from NewsAgent import NewsAgent
from VisualizationAgent import VisualizationAgent
from ReportAgent import ReportAgent

# ===========================
# 1. LLM (Groq) Configuration
# ===========================
load_dotenv()

os.environ["GROQ_MODEL"]
client = Groq(api_key=os.environ["GROQ_API_KEY"])
model_name=os.environ.get("GROQ_MODEL")

def llm(prompt: str):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

'''financial_brain = Agent(
    name="financial_orchestrator",
    instructions="""
    You coordinate the multi-agent financial system.
    Always follow the order:
    1. DataAgent
    2. AnalysisAgent
    3. NewsAgent
    4. VisualizationAgent
    5. ReportAgent
    Output should ALWAYS be clean JSON.
    """,
    markdown=False
)'''


# ============================================
# 2. Multi-Agent Workflow (AGNO Orchestration)
# ============================================
class FinancialWorkflow(Workflow):

    def run(self, ticker: str, start_date: str, end_date: str):

        print(f"\nStarting financial analysis workflow for {ticker}")

        # ---- STEP 1: Load CSV + Filter ----
        print("\n STEP 1 — Loading Data...")
        data_agent = DataAgent("master_investment_dataset.csv")
        df = data_agent.get_data(ticker, start_date, end_date)
        df = data_agent.compute_indicators(df)
        indicator_summary = data_agent.get_indicator_summary(df)

        # ---- STEP 2: Technical Analysis ----
        print("\n STEP 2 — Running Technical Analysis...")
        analysis_agent = AnalysisAgent(ticker)
        analysis_output = analysis_agent.run(df, indicator_summary)

        # ---- STEP 3: News + Sentiment ----
        print("\n STEP 3 — News Sentiment...")
        news_agent = NewsAgent(ticker)
        articles = news_agent.fetch_news(start_date, end_date)
        news_summary = news_agent.summarize_sentiment(articles)

        # ---- STEP 4: Visualization ----
        print("\n STEP 4 — Generating Charts...")
        viz_agent = VisualizationAgent(ticker)
        chart_paths = viz_agent(df, analysis_output, news_summary)

        # ---- STEP 5: LLM Summary ----
        print("\n STEP 5 — LLM Summary Generation...")
        final_summary = self.generate_summary_llm(ticker, analysis_output, news_summary)

        # ---- STEP 6: PDF Report ----
        print("\n STEP 6 — Creating PDF Report...")
        report_agent = ReportAgent()
        payload = {
            "ticker": ticker,
            "start": start_date,
            "end": end_date,
            "technical": indicator_summary,
            "trend": analysis_output["trend"],
            "score": analysis_output["score"],
            "final_signal": analysis_output["signal"],
            "sentiment": news_summary,
            "news_articles": articles,
            "summary": final_summary,
            "charts": chart_paths
        }

        pdf_path = report_agent.generate_report(payload)
        print(f"\n Report saved at: {pdf_path}")

        return {
            "pdf_path": pdf_path,
            "summary": final_summary,
            "articles": articles,
            "charts": chart_paths
        }


    # -------------------------------
    # Helper: LLM summary generation
    # -------------------------------
    def generate_summary_llm(self, ticker, analysis, sentiment):

        prompt = f"""
        You are financial Adviser,Give a clean, short financial summary for {ticker} and 
        advice the user to buy/sell and prices of the stock asked:

        Trend: {analysis['trend']}
        Score: {analysis['score']}
        Signal: {analysis['signal']}

        Sentiment Summary: {sentiment['summary']}
        Avg Sentiment: {sentiment['avg_sentiment']}
        News Count: {sentiment['news_count']}
        """

        result = llm(prompt)
        return result


# ===================================================
# 3. Public function to run workflow from main app
# ===================================================
def run_financial_agents(ticker, start_date, end_date):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    workflow = FinancialWorkflow()
    result = workflow.run(ticker, start_date, end_date)
    return result
