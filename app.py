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
        if date_unix >= 1585526400 and date_unix < 1603670400:
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
                for i in range(timestamps - count):
                    values[crypto].append(100)

            qdata = db.execute("SELECT value FROM crypto_data WHERE date_unix >= ? AND symbol = ? ORDER BY date_unix", (date_unix, crypto))
            for x in qdata:
                values[crypto].append(x)
            startvalue = values[crypto][0 + missing_values]
            values[crypto][0 + missing_values] = 100
            for y in range(1, len(values[crypto])):
                values[crypto][y] = 100 * values[crypto][y] / startvalue

        # prepare EUR baseline values
        EURvalues = []
        qdataEUR = db.execute("SELECT value FROM crypto_data WHERE date_unix >= ? AND symbol = ? ORDER BY date_unix", (date_unix, "EUR"))
        for x in qdataEUR:
            EURvalues.append(x)
        startvalue = EURvalues[0]
        EURvalues[0] = 100
        for y in range(1, len(EURvalues)):
            EURvalues[y] = 100 * EURvalues[y] / startvalue

        colors = {'BTC': '#F0544F', 'ETH': '#92DCE5', 'ADA': '#291F1E', 'LTC': '#1C6E8C', 'UNI': '#274156', 'LINK': '#FBB13C', 'XRP': '#1B998B', 'SOL': '#09BC8A', 'ATOM': '#C2E812'};
        con.commit()
        con.close()

        return render_template('index.html', colors=colors, timestamps=timestamps, EURvalues=EURvalues, values=values, selected_cryptos=selected_cryptos)

    return render_template('index.html')
