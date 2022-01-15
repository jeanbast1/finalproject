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

# function to connect database and execute query
def get_db_data(query):
    con = sqlite3.connect('cryptos.db')
    db = con.cursor()
    data = db.execute(query)
    db.commit()
    db.close()
    return data.fetchall()

@app.route('/', methods=['POST', 'GET'])
def get_crypto_data():

    # change selected crypto status in database
    if request.method == "POST" and request.form.name == "add_crypto":
        crypto_to_add = request.cookies.get('crypto')
        query = "UPDATE selected FROM crypto_selected WHERE name = ? VALUES (?), " + "True"
        get_db_data(query)

    # update start date
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
            => Add data to dict



'''
        datetime.fromtimestamp(tstamps[0])
                    print(stamp)

        crypto_data = db.execute("SELECT * FROM cryptos").fetchall()
'''

    return render_template('index.html', cryptos_data=cryptos_data)
