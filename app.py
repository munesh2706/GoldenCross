from flask import Flask, request, render_template_string
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'  # Temporary folder for uploads (Render-compatible)

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def detect_crossovers(df):
    results = []
    for symbol in df['Symbol'].unique():
        stock_data = df[df['Symbol'] == symbol].sort_values('Date')
        if len(stock_data) < 200:
            continue
        stock_data['50_EMA'] = calculate_ema(stock_data['Close'], 50)
        stock_data['200_EMA'] = calculate_ema(stock_data['Close'], 200)
        
        # Get last few rows for recent analysis
        recent = stock_data.tail(5)  # Last 5 days
        for i in range(1, len(recent)):
            prev_50 = recent['50_EMA'].iloc[i-1]
            curr_50 = recent['50_EMA'].iloc[i]
            prev_200 = recent['200_EMA'].iloc[i-1]
            curr_200 = recent['200_EMA'].iloc[i]
            
            # Just crossing: Crossed in last 1-2 days
            if (prev_50 < prev_200 and curr_50 > curr_200) or (prev_50 > prev_200 and curr_50 < curr_200):
                direction = "Bullish" if curr_50 > curr_200 else "Bearish"
                results.append((symbol, f"Just Crossed ({direction})", recent['Date'].iloc[i]))
                break  # Only report once per stock
            
            # About to cross: Within 0.5% and trending
            diff = abs(curr_50 - curr_200) / curr_200
            if diff < 0.005:  # 0.5% threshold
                if (curr_50 < curr_200 and curr_50 > recent['50_EMA'].iloc[i-1]) or (curr_50 > curr_200 and curr_50 < recent['50_EMA'].iloc[i-1]):
                    direction = "Approaching Bullish" if curr_50 < curr_200 else "Approaching Bearish"
                    results.append((symbol, direction, recent['Date'].iloc[i]))
                    break
    return results

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            try:
                df = pd.read_csv(filepath)
                df['Date'] = pd.to_datetime(df['Date'])  # Ensure date parsing
                results = detect_crossovers(df)
                os.remove(filepath)  # Clean up
                html = """
                <html>
                <head><title>NSE EMA Crossover App</title></head>
                <body>
                <h1>EMA Crossover Results</h1>
                <table border="1">
                <tr><th>Stock</th><th>Status</th><th>Date</th></tr>
                {% for stock, status, date in results %}
                <tr><td>{{ stock }}</td><td>{{ status }}</td><td>{{ date }}</td></tr>
                {% endfor %}
                </table>
                <a href="/">Upload Another File</a>
                </body>
                </html>
                """
                return render_template_string(html, results=results)
            except Exception as e:
                return f"Error processing file: {str(e)}"
        else:
            return "Invalid file. Please upload a CSV."
    
    # GET: Show upload form
    html = """
    <html>
    <head><title>NSE EMA Crossover App</title></head>
    <body>
    <h1>Upload NSE CSV for EMA Analysis</h1>
    <form method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept=".csv" required>
    <button type="submit">Analyze</button>
    </form>
    <p>Download CSV from NSE website (e.g., historical data). Ensure columns: Symbol, Date, Close.</p>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
