from flask import Flask, render_template, request, redirect
import requests as rq
import quandl as qd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/view_ticker', methods=['GET', 'POST'])
def view_ticker():
    if request.method == 'POST':
        stock = request.form['ticker']
        value = '.4'
        status = 'Close'
        if request.form.get('box1'):
            value = '.4'
            status = 'Close'
        if request.form.get('box2'):
            value = '.11'
            status = 'Adj. Close'
        if request.form.get('box3'):
            value = '.1'
            status = 'Open'
        if request.form.get('box4'):
            value = '.8'
            status = 'Adj. Open'

        mydata = qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')
        p = figure(x_axis_type = 'datetime', title = status + " Price for " + request.form['ticker'])
        p.line('Date', status, source=mydata)
        p.xaxis.axis_label = "Date"
        p.yaxis.axis_label = "Price"
        html = file_html(p, CDN, "my plot")

        return html

if __name__ == '__main__':
  app.run(port=33507)
