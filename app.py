from flask import Flask, render_template, request, redirect
import requests as rq
import quandl as qd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from datetime import datetime
import pandas as pd
import numpy as np
from pandas_datareader.data import wb


#test

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/view_ticker', methods=['GET', 'POST'])
def view_ticker():
    stock = request.form['ticker']
    start = request.form['start']
    start = datetime.strptime(start, '%Y-%m-%d')
    start = start.date()
    #print "start"
    end = request.form['end']
    end = datetime.strptime(end, '%Y-%m-%d')
    end = end.date()
    #print "end"
    value = '.4'
    status = 'Close'
    if request.form.get('box1'):
        value = '.4'
        status = 'Close'
    if request.form.get('box2'):
        value = '.11'
        status = 'Adj Close'
    if request.form.get('box3'):
        value = '.1'
        status = 'Open'
    
    mydata = wb.DataReader(stock, 'yahoo', start, end)[status]
    #mydata = qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')
    p = figure(x_axis_type = 'datetime', title = status + " Price for " + request.form['ticker'])
    p.line('Date', status, source=mydata)
    p.xaxis.axis_label = str(start)#"Date"
    p.yaxis.axis_label = "Price"
    html = file_html(p, CDN, "my plot")

    return html

if __name__ == '__main__':
  app.run()
