from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Test stocks
TEST_STOCKS = ['RELIANCE.NS', 'TCS.NS']

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def fetch_and_analyze():
    crossover_stocks = []
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=250)
        for stock in TEST_STOCKS:
            try:
                data = yf.download(stock, start=start_date, end=end_date, progress=False, timeout=10)
                if len(data) < 200:
                    continue
                data['50_EMA'] = calculate_ema(data['Close'], 50)
                data['200_EMA'] = calculate_ema(data['Close'], 200)
                if data['50_EMA'].iloc[-2] < data['200_EMA'].iloc[-2] and data['50_EMA'].iloc[-1] > data['200_EMA'].iloc[-1]:
                    crossover_stocks.append(f"{stock} - Bullish Crossover")
                elif data['50_EMA'].iloc[-2] > data['200_EMA'].iloc[-2] and data['50_EMA'].iloc[-1] < data['200_EMA'].iloc[-1]:
                    crossover_stocks.append(f"{stock} - Bearish Crossover")
            except Exception as e:
                crossover_stocks.append(f"Error with {stock}: {str(e)}")
    except Exception as e:
        crossover_stocks = [f"Global error: {str(e)}"]
    return crossover_stocks

@app.route('/')
def home():
    stocks = fetch_and_analyze()
    html = """
    <html>
    <head><title>NSE EMA Crossover App</title></head>
    <body>
    <h1>Stocks with 50 EMA Crossing 200 EMA</h1>
    <ul>
    {% for stock in stocks %}
    <li>{{ stock }}</li>
    {% endfor %}
    </ul>
    <p>Last updated: {{ time }}</p>
    </body>
    </html>
    """
    return render_template_string(html, stocks=stocks, time=datetime.now())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
