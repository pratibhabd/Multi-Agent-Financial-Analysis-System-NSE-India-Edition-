# analysis_agent.py

import numpy as np


class AnalysisAgent:
    """
    The Analysis Agent receives:
    - Clean dataset (df)
    - Technical indicators (dict)

    And produces:
    - Trend analysis
    - Strength score
    - A BUY/HOLD/SELL signal
    - Detailed commentary
    """

    def __init__(self, ticker):
        self.ticker = ticker

    # --------------------------------------------------------
    # 1. Trend Classification
    # --------------------------------------------------------
    def classify_trend(self, df):
        # slope of last 30-day close prices using linear regression
        closes = df['Close'].tail(30).values
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]

        if slope > 0.5:
            return "Uptrend"
        elif slope < -0.5:
            return "Downtrend"
        else:
            return "Sideways"

    # --------------------------------------------------------
    # 2. Indicator Interpretation Logic
    # --------------------------------------------------------
    def interpret_indicators(self, indicators):
        explanations = {}

        # RSI
        rsi = indicators['RSI']
        if rsi < 30:
            explanations['RSI'] = "RSI indicates **oversold** conditions (bullish)."
        elif rsi > 70:
            explanations['RSI'] = "RSI indicates **overbought** conditions (bearish)."
        else:
            explanations['RSI'] = "RSI is in a **neutral** range."

        # MACD
        macd = indicators['MACD']
        signal = indicators['Signal']
        if macd > signal:
            explanations['MACD'] = "MACD crossover is **bullish**."
        else:
            explanations['MACD'] = "MACD crossover is **bearish**."

        # Bollinger Band
        close = indicators['Close']
        bb_upper = indicators['BB_upper']
        bb_lower = indicators['BB_lower']

        if close >= bb_upper:
            explanations['BB'] = "Price touching **upper band** (possible reversal)."
        elif close <= bb_lower:
            explanations['BB'] = "Price touching **lower band** (potential bounce)."
        else:
            explanations['BB'] = "Price is within Bollinger Bands (normal volatility)."

        return explanations

    # --------------------------------------------------------
    # 3. Stock Strength Scoring
    # --------------------------------------------------------
    def score_stock(self, indicators):
        score = 50  # neutral starting point

        # RSI scoring
        rsi = indicators['RSI']
        if 30 < rsi < 70:
            score += 10
        elif rsi <= 30:
            score += 15
        elif rsi >= 70:
            score -= 10

        # MACD scoring
        if indicators['MACD'] > indicators['Signal']:
            score += 10
        else:
            score -= 10

        # Bollinger scoring
        close = indicators['Close']
        if close < indicators['BB_lower']:
            score += 10  # oversold bounce
        if close > indicators['BB_upper']:
            score -= 10  # overbought

        return max(0, min(100, score))

    # --------------------------------------------------------
    # 4. Final Signal (BUY / HOLD / SELL)
    # --------------------------------------------------------
    def generate_signal(self, score, trend):
        if score >= 70 and trend == "Uptrend":
            return "BUY"
        elif score <= 40 and trend == "Downtrend":
            return "SELL"
        else:
            return "HOLD"

    # --------------------------------------------------------
    # 5. Master function: produces final analysis
    # --------------------------------------------------------
    def run(self, df, indicators):
        trend = self.classify_trend(df)
        indicator_explanations = self.interpret_indicators(indicators)
        score = self.score_stock(indicators)
        signal = self.generate_signal(score, trend)

        analysis = {
            "ticker": self.ticker,
            "trend": trend,
            "score": score,
            "signal": signal,
            "indicator_explanations": indicator_explanations
        }
        return analysis
