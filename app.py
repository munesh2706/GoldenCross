from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Top 50 NSE stocks (by market cap/popularity; add/remove as needed)
NSE_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS', 'AXISBANK.NS',
    'MARUTI.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS', 'HCLTECH.NS', 'WIPRO.NS',
    'ULTRACEMCO.NS', 'NESTLEIND.NS', 'POWERGRID.NS', 'NTPC.NS', 'GRASIM.NS',
    'JSWSTEEL.NS', 'TITAN.NS', 'DRREDDY.NS', 'SUNPHARMA.NS', 'CIPLA.NS',
    'TECHM.NS', 'DIVISLAB.NS', 'ADANIPORTS.NS', 'COALINDIA.NS', 'BPCL.NS',
    'ONGC.NS', 'SHREECEM.NS', 'HEROMOTOCO.NS', 'BRITANNIA.NS', 'EICHERMOT.NS',
    'APOLLOHOSP.NS', 'UPL.NS', 'M&M.NS', 'INDUSINDBK.NS', 'BAJAJ-AUTO.NS',
    'TATACONSUM.NS', 'HINDALCO.NS', 'ADANIGREEN.NS', 'PIDILITIND.NS', 'BERGEPAINT.NS',
    'DABUR.NS', 'HAVELLS.NS', 'GODREJCP.NS', 'MARICO.NS', 'COLPAL.NS'
]

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def fetch_and_analyze():
    crossover_stocks = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=250)  # 250 days for EMA calc
    for stock in NSE_STOCKS:
        try:
            data = yf.download(stock, start=start_date, end=end_date, progress=False, timeout=10)
            if len(data) < 200:
                continue  # Skip if not enough data
            data['50_EMA'] = calculate_ema(data['Close'], 50)
            data['200_EMA'] = calculate_ema(data['Close'], 200)
            latest_50 = data['50_EMA'].iloc[-1]
            prev_50 = data['50_EMA'].iloc[-2]
            latest_200 = data['200_EMA'].iloc[-1]
            prev_200 = data['200_EMA'].iloc[-2]
            if prev_50 < prev_200 and latest_50 > latest_200:
                crossover_stocks.append((stock, "Bullish Crossover"))
            elif prev_50 > prev_200 and latest_50 < latest_200:
                crossover_stocks.append((stock, "Bearish Crossover"))
        except Exception as e:
            crossover_stocks.append((stock, f"Error: {str(e)}"))
    return crossover_stocks

@app.route('/')
def home():
    stocks = fetch_and_analyze()
    html = """
    <html>
    <head>
        <title>NSE EMA Crossover App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Stocks with 50 EMA Crossing 200 EMA (Top 50 NSE)</h1>
        <table>
            <tr><th>Stock</th><th>Status</th></tr>
            {% for stock, status in stocks %}
            <tr><td>{{ stock }}</td><td>{{ status }}</td></tr>
            {% endfor %}
        </table>
        <p>Last updated: {{ time }}</p>
        <p>Note: Analysis based on recent data. Refresh page for latest.</p>
    </body>
    </html>
    """
    return render_template_string(html, stocks=stocks, time=datetime.now())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
