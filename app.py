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

    # change selected crypto status in database
    if request.method == 'POST' and "form1" in request.form:
        crypto_to_add = request.form.get('crypto')
        db.execute("UPDATE crypto_selected SET selected = 1 WHERE symbol = ?;", [crypto_to_add])
        con.commit()
        con.close()
        return redirect("/")

    # change selected crypto status in database
    if request.method == 'POST' and "form3" in request.form:
        crypto_to_remove = request.form.get('crypto_to_unselect')
        db.execute("UPDATE crypto_selected SET selected = 0 WHERE symbol = ?;", [crypto_to_remove])
        con.commit()
        con.close()
        return redirect("/")

    # change selected startdate in database
    if request.method == 'POST' and "form2" in request.form:
        date = request.form.get('date')
        date_unix = (int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())) + 3600) * 1000
        db.execute("UPDATE date_selected SET date = ?, unix = ?", (date, date_unix))
        con.commit()
        con.close()
        return redirect("/")

    # change selected crypto status in database
    if request.method == 'GET':
        selected_cryptos = []
        values = {}
        qcryptos = db.execute("SELECT symbol FROM crypto_selected WHERE selected = 1")
        for row in qcryptos:
            selected_cryptos.append(row)
        qdate = db.execute("SELECT date FROM date_selected")
        for row in qdate:
            date_selected = row
        date_unix = (int(time.mktime(datetime.datetime.strptime(date_selected, "%Y-%m-%d").timetuple())) + 3600) * 1000

        # add the timestamps (dates) for the values
        timestamps = []
        qdata = db.execute("SELECT DISTINCT date FROM crypto_data WHERE unix >= ? ORDER BY unix", [date_unix])
        for timestamp in qdata:
            timestamps.append(timestamp)

        # add the values and rebase values to 100
        for crypto in selected_cryptos:
            values[crypto] = []
            qdata = db.execute("SELECT value FROM crypto_data WHERE unix >= ? AND symbol = ? ORDER BY unix", (date_unix, crypto))
            for x in qdata:
                values[crypto].append(x)
            startvalue = values[crypto][0]
            values[crypto][0] = 100
            for y in range(1, len(values[crypto])):
                values[crypto][y] = 100 * values[crypto][y] / startvalue

        colors = {'BTC': '#F0544F', 'ETH': '#92DCE5', 'ADA': '#291F1E', 'LTC': '#1C6E8C', 'UNI': '#274156', 'LINK': '#FBB13C', 'XRP': '#1B998B', 'SOL': '#09BC8A', 'DOT': '#C2E812'};
        con.commit()
        con.close()

        return render_template('index.html', colors=colors, timestamps=timestamps, values=values, date_selected=date_selected, selected_cryptos=selected_cryptos)

    return render_template('index.html')
