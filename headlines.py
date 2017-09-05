import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib
import urllib.parse
import urllib.request

DEFAULTS = {
    'publication': 'bbc',
    'city': 'London,UK',
    'currency_from': 'GBP',
    'currency_to': 'USD'
}

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id" \
               "=017c282c3355405a94a55dae16aee15e"

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&' \
              'units=metric&appid=cb932829eacb6a0e9ee4f38bfbf112ed'

app = Flask(__name__)

RSS_FEED = {"bbc": "http://feeds.bbci.co.uk/news/rss.xml",
            "cnn": "http://rss.cnn.com/rss/edition.rss",
            "fox": "http://feeds.foxnews.com/foxnews/latest",
            "iol": "http://www.iol.co.za/cmlink/1.640"}


# @app.route("/")
# @app.route("/bbc")
# def bbc():
#     return get_news('bbc')
#
#
# @app.route("/cnn")
# def cnn():
#     return get_news('cnn')


@app.route("/")
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    # get currency_from and currency_to
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate,currencies = get_rate(currency_from, currency_to)
    return render_template('home.html',
                           articles=articles,
                           weather=weather,
                           rate=rate,
                           currency_from=currency_from,
                           currency_to=currency_to,
                           currencies=sorted(currencies))


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    weather = get_weather("london,uk")
    return feed['entries']


def get_weather(query):
    api_url = WEATHER_URL
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read().decode('utf-8')
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   "country": parsed['sys']['country']}
    return weather


def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read().decode('utf-8')
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())


if __name__ == '__main__':
    app.run(port=5000, debug=True)

