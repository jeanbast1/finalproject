from flask import Flask, render_template, request
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


url = 'https://api.kraken.com/0/public/OHLC?pair='


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

    # change selected startdate in database
    if request.method == 'POST' and "form2" in request.form:
        date = request.form.get('date')
        date_unix = (int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())) + 3600) * 1000
        print(date_unix)
        db.execute("UPDATE date_selected SET date = ?, unix = ?", (date, date_unix))

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

        for crypto in selected_cryptos:
            values[crypto] = []
            qdata = db.execute("SELECT value FROM crypto_data WHERE unix >= ? AND symbol = ? ORDER BY unix LIMIT 5", (date_unix, crypto))
            for row in qdata:
                values[crypto].append(row)


        return render_template('index.html', values=values, date_selected=date_selected, selected_cryptos=selected_cryptos)

    # disconnect database
    con.commit()
    con.close()

    return render_template('index.html')


'''    # update start date
    elif request.method == "POST" and request.form.name == "change_date":
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")
        query = "UPDATE year, month, day FROM date_selected VALUES (?,?,?), " + year + "," + month + "," + day
        get_db_data(query)

    # get graph data from database
    elif request.method == "GET":

        query_crypto = "SELECT crypto FROM crypto_selected WHERE selected = True"
        cryptos = get_db_data(query_crypto)
        query_date = "SELECT year, month, day FROM date_selected"
        date = get_db_data(query_date)

        #get historical values data
        cryptos_data = {}
        for crypto in cryptos:
            query = "SELECT value FROM crypto_data WHERE crypto = ? AND year >= ? AND month >= ? AND day >= ?", crypto , date
            crypto_data = get_db_data(query)


        datetime.fromtimestamp(tstamps[0])
                    print(stamp)

        crypto_data = db.execute("SELECT * FROM cryptos").fetchall()
'''
