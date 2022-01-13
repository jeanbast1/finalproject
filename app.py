from flask import Flask, render_template, request
import requests
from datetime import datetime

import sqlite3
con = sqlite3.connect('cryptos.db')
db = con.cursor()


# db.execute("CREATE TABLE [IF NOT EXISTS] crypto_data (year integer, month integer, day integer, value real)")

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


url = 'https://api.kraken.com/0/public/OHLC?pair='

@app.route('/', methods=['POST', 'GET'])
def get_crypto_data():
    if request.method == "POST":
        crypto = request.form.get("cryptos")
        resp = requests.get(url + crypto + 'EUR&interval=1440&since=1639782000').json()
        result = resp['result']

        # iterate through keys of result
        for key in result:
            # if key is crypto-currency pair
            if crypto in key:
                # iterate through key values and create data dict
                result = result[key]
                for date in result:
                    stamp = datetime.fromtimestamp(date[0])
                    year = datetime.stamp.year()
                    print(year)
                    db.execute("INSERT INTO cryptos (year, month, day, value) VALUES(?,?,?,?)", int(stamp.datetime.year), int(stamp.datetime.month), int(stamp.datetime.day), float(date[1]))
                    # dates.append(stamp)
                    # prices.append(float(date[1]))
        crypto_data = db.execute("SELECT * FROM cryptos")

        return render_template('index.html', crypto_data=crypto_data)
    else:
        return render_template("index.html")
