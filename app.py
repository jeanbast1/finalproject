from flask import Flask, render_template, request, redirect
import requests
import time
import datetime
import sqlite3

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/update')
def update_db():
    if request.method == 'GET':

        # connect db
        con = sqlite3.connect('cryptodatabase.db')
        con.row_factory = lambda cursor, row: row[0]
        db = con.cursor()

        #check last value in database:
        current_date_unix = db.execute("SELECT unix FROM dates ORDER BY unix DESC LIMIT 1")
        for row in current_date_unix:
            current_date_unix = row

        # today's date to unix
        dt = datetime.date.today()
        unixtime = round(time.mktime(dt.timetuple())) + 3600

        # update dates in database
        unix_to_add = current_date_unix + (60 * 60 * 24)
        unix_timestamps = []
        dates = []
        while unix_to_add <= unixtime:
            unix_timestamps.append(unix_to_add)
            dates.append(datetime.datetime.fromtimestamp(unix_to_add).strftime('%Y-%m-%d'))
            unix_to_add = unix_to_add + (60 * 60 * 24)

        for i in range(len(unix_timestamps)):
            db.execute("INSERT INTO dates (unix, date, selected) VALUES(?, ?, ?)", (unix_timestamps[i], dates[i], 0))
            con.commit()

        # update crypto values
        all_cryptos = []
        get_cryptos = db.execute("SELECT symbol FROM crypto_selected")
        for crypto in get_cryptos:
            all_cryptos.append(crypto)

        url = "https://api.kraken.com/0/public/OHLC?pair="
        for crypto in all_cryptos:
            response = requests.get(url + crypto + "USD&interval=1440&since=" + str(current_date_unix))
            kraken_data = response.json()
            if "result" in kraken_data:
                kraken_data = kraken_data["result"]
                kraken_data.pop("last")
                for row in kraken_data:
                    if len(kraken_data[row]) > 1:
                        for i in range(len(kraken_data[row])):
                            db.execute("INSERT INTO crypto_data (value, symbol, date_unix) VALUES(?,?,?)", (kraken_data[row][i][1], crypto, kraken_data[row][i][0]))
                            con.commit()

        con.close()
        return render_template("update.html")

@app.route('/', methods=['POST', 'GET'])
def get_crypto_data():

    # connect database
    con = sqlite3.connect('cryptodatabase.db')
    con.row_factory = lambda cursor, row: row[0]
    db = con.cursor()

    # mark crypto as selected in database
    if request.method == 'POST' and "form1" in request.form:
        crypto_to_add = request.form.get('crypto')
        db.execute("UPDATE crypto_selected SET selected = 1 WHERE symbol = ?;", [crypto_to_add])
        con.commit()
        con.close()
        return redirect("/")

    # remove selected crypto status in database
    if request.method == 'POST' and "form3" in request.form:
        crypto_to_remove = request.form.get('crypto_to_unselect')
        db.execute("UPDATE crypto_selected SET selected = 0 WHERE symbol = ?;", [crypto_to_remove])
        con.commit()
        con.close()
        return redirect("/")

    # change selected startdate in database
    if request.method == 'POST' and "form2" in request.form:
        date = request.form.get('date')
        date_unix = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())) + 3600
        if (date_unix >= 1585526400 and date_unix <= 1603584000) or (date_unix >= 1616976000 and date_unix <= 1635638400):
            date_unix = date_unix + 3600
        db.execute("UPDATE dates SET selected = 0")
        con.commit()
        db.execute("UPDATE dates SET selected = 1 WHERE unix = ?", [date_unix])
        con.commit()
        con.close()
        return redirect("/")

    # prep data for render
    if request.method == 'GET':
        selected_cryptos = []
        date_unix = 0
        qcryptos = db.execute("SELECT symbol FROM crypto_selected WHERE selected = 1")
        for row in qcryptos:
            selected_cryptos.append(row)
        qdate = db.execute("SELECT unix FROM dates WHERE selected = 1")
        for row in qdate:
            date_unix = row

        # add the timestamps (dates) for the values
        timestamps = []
        qdata = db.execute("SELECT DISTINCT date FROM dates WHERE unix >= ? ORDER BY unix", [date_unix])
        for timestamp in qdata:
            timestamps.append(timestamp)

        # add the values and rebase values to 100
        values = {}
        for crypto in selected_cryptos:
            values[crypto] = []
            qdata = db.execute("SELECT value FROM crypto_data WHERE date_unix >= ? AND symbol = ? ORDER BY date_unix", (date_unix, crypto))

            # count number of values
            count = 0
            for row in qdata:
                count = count + 1

            missing_values = len(timestamps) - count

            if missing_values > 0:
                for i in range(missing_values):
                    values[crypto].append(100)

            qdata = db.execute("SELECT value FROM crypto_data WHERE date_unix >= ? AND symbol = ? ORDER BY date_unix", (date_unix, crypto))
            for x in qdata:
                values[crypto].append(x)
            startvalue = values[crypto][missing_values]
            values[crypto][missing_values] = 100
            for y in range(1 + missing_values, len(values[crypto])):
                values[crypto][y] = 100 * values[crypto][y] / startvalue

        colors = {'BTC': '#F0544F', 'ETH': '#92DCE5', 'ADA': '#291F1E', 'LTC': '#1C6E8C', 'UNI': '#274156', 'LINK': '#FBB13C', 'XRP': '#1B998B', 'SOL': '#09BC8A', 'ATOM': '#C2E812', 'SHIB': '#66D24E', 'DOT': '#77B6EA', 'DOGE': '#EE4266', 'ALGO': '#D5B942'};

        # Push latest date in database to template
        max_date = db.execute("SELECT date FROM dates ORDER BY unix DESC LIMIT 1")
        for row in max_date:
            max_date = row

        con.commit()
        con.close()

        return render_template('index.html', max_date=max_date, colors=colors, timestamps=timestamps, values=values, selected_cryptos=selected_cryptos)

    return render_template('index.html')
