# YOUR PROJECT TITLE

#### Video Demo:  <URL HERE>

#### Description:

My project is called Crypto price evolution and is a web-based application that allows to compare fluctuations in the valuation of cryptocurrencies over time.

##### Why this project ?

I sometimes invest in cryptocurrencies and have often found it difficult to visualize how cryptocurrencies valuation evolved over time and especially how they evolved when compared to one another.

##### Installation

I chose to develop this program outside of the CS50 IDE to better understand what was needed in order to run code on my own computer.
I installed the text editor Atom (which makes it easy to interact with Github). I used version management with Github.
I installed some Python libraries such as "Flask", "requests" directly on my computer which required the installation of Python3 to function properly as well as some installation functionalities like "pip".
I also installed sqlite3 to communicate with my database.
I created my database and imported data into it directly with my mac Terminal app which can be viewed in Atom (I used the .csv import mode to import the large data files that needed to be stored)

##### How it works

The program consists of a SQL database ('/cryptodatabase.db') storing all the historical values of the 10 or so cryptocurrencies I have decided to include in this project. These historical values where retrieved from Binance and Kraken (both are online cryptocurrency trading services with open access to historical data).

A Python/Flask application ('/app.py') is then built on top of this database to access the data dynamically and prepare it in order to render it correctly in a visual fashion on a webpage. The Python app does a few things in order to have clean data that can be used on the webpage: first, the app retrieves the correct data and dates from the database (based on user inputs on the webpage) and stores it in variables. The data is then modified as to make sure the values are rebased at 100 at the start of the analysis timeframe that is selected by the user. This allows cryptocurrencies to be viewed in terms of percentage of evolution over time rather than through trading value (plotting Bitcoin which is worth over 40k$ and a crypto like Dogecoin which is worth less than 1$ on the same chart does not yield much information as variations are barely noticeable given the difference in value)

The webpage (HTML/CSS/Javascript) ('/templates') uses some Jinja syntax to retrieve information from the Flask app. The webpages contains two forms that allow the user to select one or multiple cryptocurrencies to compare as well as a start date for the cryptocurrencies comparison. This information is then sent back to the Python app and stored in the database before the page is reloaded based on the novel information requested by the user.

The webpage uses Chart.js to render the data visually using a line-chart. The data from the database, prepared with Python, is passed to the webapp with Flask/Jinja and rearranged to fit the requirement of Chart.js. Three data types are passed to the webapp: crypto value data, colors for the line charts of each crypto, dates to use as series on the x-axis.

Finally, the webapp contains another hidden URL ('/update') that uses the kraken.com API to retrieve new values since the last time the app was used. This URL has a different path in the Flask app which is used to make the API calls (one per cryptocurrency) and to prepare the data that is received so that it can fit correctly in the database. The API reponse is formatted as a JSON object and then parsed to get the appropriate data and discard unused data. This path also manipulated the dates so that unix Epoch timestamps can be converted to readable dates.

The static folder holds an image used on the webapp and the ('/styles.css') file holding the CSS parameters used to style the HTML template pages.

##### Configuration

A virtual environment has to be created in order for Flask to function properly. Before running the program, the following command has to be run in terminal: ". venv/bin/activate" to activate the virtual environment.
The "/venv" folder stores the necessary files to configure the virtual environment.

Using sqlite3 outside of CS50 IDE: some core functionalities used in CS50's IDE where not available at first and took some time to re-implement. Retrieving data from the cursor object is done using for loops. The database connection is closed after all the data is requested.

Manipulating dates: the API endpoints used to retrieve data uses unix Epoch timestamps linked to the cryptocurrency values. The Python app and SQL database use both unix timestamps (since they are very convenient to store as integers and to order from smallest to largest) and dates readable by humans (stored as strings and displayed on the graph).

Preparing data for charting: the correct format that is expected from Chart.js to display the data correctly (both for the series labels and the chart values) is rather complex to understand. In the program the data is parsed using Jinja syntax in the HTML/JS template to fit the requirements.
