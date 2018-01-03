from flask import Flask, render_template, request, redirect
import requests as rq
import Quandl as qd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

app = Flask(__name__)

DUMMY = range(5)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/view_ticker', methods=['GET', 'POST'])
def view_ticker():
    stock = request.form['ticker']
    value = 0.4
    if request.method == 'POST':
        if 'close' in request.form:
            value = "0.4"
        if 'adj_close' in request.form:
            value = "0.10"
        if 'open' in request.form:
            value = "0.1"
        if 'adj_open' in request.form:
            value = "0.7"

        mydata =  qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')
        plot = figure(plot_width=400, plot_height=400)
        p.line = DUMMY
        html = file_html(plot, CDN, "my plot") 

        return html

if __name__ == '__main__':
  app.run(host='0.0.0.0')
