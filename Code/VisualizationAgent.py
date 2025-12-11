# visualization_tool.py
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

class VisualizationAgent:
    def __init__(self,ticker, output_dir="charts"):
        self.output_dir = output_dir
        self.ticker=ticker
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_price_signals(self, df, analysis):
        """
        Price chart with BUY/HOLD/SELL signals
        """
        plt.figure(figsize=(12,6))
        plt.plot(df['Date'], df['Close'], label='Close Price', color='blue')

        # Mark the signal on the last day as example
        signal = analysis['signal']
        color = {'BUY':'green', 'SELL':'red', 'HOLD':'orange'}.get(signal, 'gray')
        plt.scatter(df['Date'].iloc[-1], df['Close'].iloc[-1], color=color, s=100, label=f'Signal: {signal}')

        plt.title(f"{analysis['ticker']} Price with Signal ({analysis['trend']})")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        path = os.path.join(self.output_dir, f"{analysis['ticker']}_price_signal.png")
        plt.savefig(path)
        plt.close()
        return path

    def plot_indicators(self, df):
        """
        Plot MACD, RSI, Bollinger Bands
        """
        paths = {}

        # ----- MACD -----
        plt.figure(figsize=(12,4))
        plt.plot(df['Date'], df['MACD'], label='MACD', color='blue')
        plt.plot(df['Date'], df['Signal'], label='Signal', color='red')
        plt.title("MACD Indicator")
        plt.xlabel("Date")
        plt.ylabel("MACD")
        plt.legend()
        plt.grid(True)
        macd_path = os.path.join(self.output_dir, "MACD.png")
        plt.savefig(macd_path)
        plt.close()
        paths['MACD'] = macd_path

        # ----- RSI -----
        plt.figure(figsize=(12,4))
        plt.plot(df['Date'], df['RSI'], label='RSI', color='purple')
        plt.axhline(70, color='red', linestyle='--', label='Overbought')
        plt.axhline(30, color='green', linestyle='--', label='Oversold')
        plt.title("RSI Indicator")
        plt.xlabel("Date")
        plt.ylabel("RSI")
        plt.legend()
        plt.grid(True)
        rsi_path = os.path.join(self.output_dir, "RSI.png")
        plt.savefig(rsi_path)
        plt.close()
        paths['RSI'] = rsi_path

        # ----- Bollinger Bands -----
        plt.figure(figsize=(12,4))
        plt.plot(df['Date'], df['Close'], label='Close', color='blue')
        plt.plot(df['Date'], df['BB_upper'], label='Upper Band', color='red', linestyle='--')
        plt.plot(df['Date'], df['BB_lower'], label='Lower Band', color='green', linestyle='--')
        plt.title("Bollinger Bands")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        bb_path = os.path.join(self.output_dir, "BollingerBands.png")
        plt.savefig(bb_path)
        plt.close()
        paths['BollingerBands'] = bb_path

        return paths

    def plot_profit_simulation(self, df, analysis, starting_capital=10000):
        """
        Simulate capital growth if user follows BUY/HOLD/SELL signals
        """
        capital = starting_capital
        position = 0
        capital_over_time = []

        # Simple simulation: apply the last signal over the entire df as example
        for price in df['Close']:
            if analysis['signal'] == "BUY" and position == 0:
                position = capital / price #How many shares you can buy with your available money
                capital = 0
            elif analysis['signal'] == "SELL" and position > 0:
                capital = position * price
                position = 0
            capital_over_time.append(capital + (position * price if position > 0 else 0))

        plt.figure(figsize=(12,6))
        plt.plot(df['Date'], capital_over_time, label='Simulated Capital', color='green')
        plt.title(f"{analysis['ticker']} Capital Growth Simulation")
        plt.xlabel("Date")
        plt.ylabel("Capital ($)")
        plt.grid(True)
        plt.legend()

        path = os.path.join(self.output_dir, f"{analysis['ticker']}_profit_simulation.png")
        plt.savefig(path)
        plt.close()
        return path

    def plot_sentiment(self, sentiment_summary):
        """
        Plot news sentiment summary if available
        """
        plt.figure(figsize=(8,4))
        sentiment_score = sentiment_summary.get('avg_sentiment', 0)
        plt.bar(['Sentiment'], [sentiment_score], color='blue')
        plt.ylim(-1,1)
        plt.title("Average News Sentiment")
        path = os.path.join(self.output_dir, "news_sentiment.png")
        plt.savefig(path)
        plt.close()
        return path

    def __call__(self, df, analysis, sentiment_summary=None):
        """
        Generate all charts and return paths
        """
        chart_paths = {}
        chart_paths['price_signal'] = self.plot_price_signals(df, analysis)
        chart_paths['indicators'] = self.plot_indicators(df)
        chart_paths['profit'] = self.plot_profit_simulation(df, analysis)
        if sentiment_summary:
            chart_paths['sentiment'] = self.plot_sentiment(sentiment_summary)
        return chart_paths
