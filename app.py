from flask import Flask, render_template, request
import requests
from datetime import datetime
import sqlite3

# db.execute("CREATE TABLE IF NOT EXISTS crypto_data (year integer, month integer, day integer, value real)")

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

    con = sqlite3.connect('cryptos.db')
    db = con.cursor()

    if request.method == "POST":
        crypto = request.form.get("cryptos")
        resp = requests.get(url + crypto + 'EUR&interval=1440&since=1641859200').json()
        result = resp['result']

        print(result)
        # iterate through keys of result
        for key in result:
            # if key is crypto-currency pair
            if crypto in key:
                # iterate through key values and create data dict
                result = result[key]
                for tstamps in result:
                    stamp = datetime.fromtimestamp(tstamps[0])
                    print(stamp)
                    db.execute("INSERT INTO cryptos (key, year, month, day, value) VALUES (?,?,?,?,?)", (int(str(stamp.year)+str(stamp.month)+str(stamp.day)), int(stamp.year), int(stamp.month), int(stamp.day), float(tstamps[1])))
                    # dates.append(stamp)
                    # prices.append(float(date[1]))
                    con.commit()
        crypto_data = db.execute("SELECT * FROM cryptos")
        for row in crypto_data:
            print(row)

        return render_template('index.html', crypto_data=crypto_data)
    else:
        return render_template("index.html")
