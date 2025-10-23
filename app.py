from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello, NSE EMA App is Working!</h1><p>If you see this, Flask is running.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
