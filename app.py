from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import schedule
import time
import threading

app = Flask(__name__)

# Define stock lists (Nifty 50, Bank Nifty, Nifty 100 - using Yahoo symbols)
NIFTY_50 = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 'HINDUNILVR.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS', 'HCLTECH.NS', 'ASIANPAINT.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS', 'WIPRO.NS', 'TECHM.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS', 'COALINDIA.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'GRASIM.NS', 'SHREECEM.NS', 'CIPLA.NS', 'DRREDDY.NS', 'SUNPHARMA.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS', 'INDUSINDBK.NS', 'SBIN.NS', 'ADANIPORTS.NS', 'ADANIGREEN.NS', 'ADANITRANS.NS', 'DIVISLAB.NS', 'TATACONSUM.NS', 'BRITANNIA.NS', 'APOLLOHOSP.NS', 'UPL.NS', 'HINDALCO.NS', 'VEDL.NS', 'EICHERMOT.NS', 'M&M.NS', 'BAJAJFINSV.NS', 'TITAN.NS', 'DMART.NS']
BANK_NIFTY = ['HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'INDUSINDBK.NS', 'SBIN.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS', 'PNB.NS', 'BANDHANBNK.NS', 'RBLBANK.NS', 'CITYUNION.NS']
NIFTY_100 = NIFTY_50 + ['GODREJCP.NS', 'BERGEPAINT.NS', 'PIDILITIND.NS', 'DABUR.NS', 'MARICO.NS', 'COLPAL.NS', 'PGHH.NS', 'HAVELLS.NS', 'WHIRLPOOL.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 'CROMPTON.NS', 'AMBER.NS', 'KAJARIACER.NS', 'SOMANYCERA.NS', 'CENTURYPLY.NS', 'GREENPLY.NS', 'KITEX.NS', 'WELSPUNIND.NS', 'VTL.NS', 'RITES.NS', 'IRFC.NS', 'RVNL.NS', 'GMRINFRA.NS', 'NBCC.NS', 'HUDCO.NS', 'RECLTD.NS', 'PFC.NS', 'NLCINDIA.NS', 'NHPC.NS', 'SJVN.NS', 'NTPC.NS', 'GAIL.NS', 'PETRONET.NS', 'IGL.NS', 'GUJGASLTD.NS', 'MGL.NS', 'TATAPOWER.NS', 'ADANIENSOL.NS', 'ADANIPOWER.NS', 'JSWENERGY.NS', 'NATIONALUM.NS', 'HINDZINC.NS', 'MOIL.NS', 'COCHINSHIP.NS', 'GESHIP.NS', 'MAZDOCK.NS', 'BALKRISIND.NS', 'GRAPHITE.NS', 'HBLPOWER.NS', 'SJVN.NS']

# Remove duplicates
ALL_STOCKS = list(set(NIFTY_50 + BANK_NIFTY + NIFTY_100))

# Global variable to store results
crossover_stocks = []

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def fetch_and_analyze():
    global crossover_stocks
    crossover_stocks = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=300)  # Enough for 200 EMA

    for stock in ALL_STOCKS:
        try:
            data = yf.download(stock, start=start_date, end=end_date, progress=False)
            if len(data) < 200:
                continue
            data['50_EMA'] = calculate_ema(data['Close'], 50)
            data['200_EMA'] = calculate_ema(data['Close'], 200)
            
            # Check for crossover (50 EMA crossing 200 EMA)
            if data['50_EMA'].iloc[-2] < data['200_EMA'].iloc[-2] and data['50_EMA'].iloc[-1] > data['200_EMA'].iloc[-1]:
                crossover_stocks.append(f"{stock} - Bullish Crossover")
            elif data['50_EMA'].iloc[-2] > data['200_EMA'].iloc[-2] and data['50_EMA'].iloc[-1] < data['200_EMA'].iloc[-1]:
                crossover_stocks.append(f"{stock} - Bearish Crossover")
        except Exception as e:
            print(f"Error with {stock}: {e}")
            continue

# Schedule daily run (e.g., 4 PM IST - adjust as needed)
def run_scheduler():
    schedule.every().day.at("16:00").do(fetch_and_analyze)  # 4 PM IST
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in a thread
threading.Thread(target=run_scheduler, daemon=True).start()

@app.route('/')
def home():
    fetch_and_analyze()  # Manual trigger for testing
    html = """
    <html>
    <head><title>NSE EMA Crossover App</title></head>
    <body>
    <h1>Stocks with 50 EMA Crossing 200 EMA (Previous Day)</h1>
    <ul>
    {% for stock in stocks %}
    <li>{{ stock }}</li>
    {% endfor %}
    </ul>
    <p>Last updated: {{ time }}</p>
    </body>
    </html>
    """
    return render_template_string(html, stocks=crossover_stocks, time=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
