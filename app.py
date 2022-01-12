from flask import Flask, Markup, redirect, render_template, request, session
import requests
from datetime import datetime

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

''' url_for('static', filename='style.css') '''

url = 'https://api.kraken.com/0/public/OHLC?pair='

@app.route('/', methods=['POST', 'GET'])
def get_crypto_data():
    if request.method == "POST":
        crypto = request.form.get("cryptos")
        resp = requests.get(url + crypto + 'EUR&interval=1440&since=1639782000').json()
        result = resp['result']
        dates = []
        prices = []
        # iterate through keys of result
        for key in result:
            # if key is crypto-currency pair
            if crypto in key:
                # iterate through key values and create data dict
                result = result[key]
                for date in result:
                    stamp = datetime.fromtimestamp(date[0])
                    stamp = str(datetime.date(stamp))
                    dates.append(stamp)
                    prices.append(float(date[1]))

        return render_template('index.html', dates=dates, prices=prices)
    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)

'''
# Create and connect database
conn = sqlite3.connect('cs50final_database.db')
db = conn.cursor()
'''
