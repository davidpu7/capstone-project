from flask import Flask, render_template, request, redirect
import requests as rq
import quandl as qd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, HoverTool,CrosshairTool
from bokeh.core.properties import value
from datetime import datetime
import pandas as pd
import numpy as np
from pandas_datareader.data import DataReader
from datetime import datetime
from statsmodels import api as sm 

#test

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/stock_predict', methods=['GET', 'POST'])
def stock_predict():
    if request.method == 'POST':
        # do stuff when the form is submitted
        
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('stock_predict.html')

@app.route('/view_ticker', methods=['GET', 'POST'])
def view_ticker():
    stock = request.form['ticker']
    #print stock
    start = request.form['start']
    start = datetime.strptime(start, '%Y-%m-%d')
    start = start.date()
    #print request.form['start']
    end = request.form['end']
    end = datetime.strptime(end, '%Y-%m-%d')
    end = end.date()
    #print "end"
    value = '.4'
    status = 'Close'

#    if request.form.get('box1'):
#        value = '.4'
#        status = 'Close'
#    if request.form.get('box2'):
#        value = '.11'
#        status = 'Adj Close'
#    if request.form.get('box3'):
#        value = '.1'
#        status = 'Open'
     
    df = DataReader(stock, 'yahoo', start, end)
    #mydata = qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')
    
    df.reset_index(inplace=True,drop=False)
    df['changepercent'] = df.Close.pct_change()*100
    seqs=np.arange(df.shape[0]) 
    df["seq"]=pd.Series(seqs)
    df["Date"] = pd.to_datetime(df["Date"])
    df['Date']=df['Date'].apply(lambda x: x.strftime('%Y/%m/%d'))
    df['changepercent']=df['changepercent'].apply(lambda x: str(round(x,2))+"%")
    df['mid']=df.apply(lambda x:(x['Open']+x['Close'])/2,axis=1)
    df['height']=df.apply(lambda x:abs(x['Close']-x['Open'] if x['Close']!=x['Open'] else 0.001),axis=1)
    
    inc = df.Close > df.Open
    dec = df.Open > df.Close
    w=0.5
    
    #This is where ARIMA starts
    df['Natural Log'] = df['Close'].apply(lambda x: np.log(x))
    price_matrix = df['Close'].as_matrix()
    model = sm.tsa.ARIMA(price_matrix, order=(1, 0, 0))
    results = model.fit(disp=-1)
    df['Forecast'] = results.fittedvalues

    #use ColumnDataSource to pass in data for tooltips
    sourceInc=ColumnDataSource(ColumnDataSource.from_df(df.loc[inc]))
    sourceDec=ColumnDataSource(ColumnDataSource.from_df(df.loc[dec]))    
    #will not need this one because we are putting a separate hoover to the forecast line
    #sourceforecast=ColumnDataSource(ColumnDataSource.from_df(df.loc[:]))


    #the values for the tooltip come from ColumnDataSource
    hover = HoverTool(
        names=['source_Inc', 'source_Dec'],
        tooltips=[
            ("Date", "@Date"),
            ("Open", "@Open"),
            ("Close", "@Close"),
            ("High", "@High"),
            ("Low", "@Low"),
            ("Percent", "@changepercent"),
	    ("Volume", "@Volume"),
           # ("Forecast", "@Forecast"),
        ]
    )

    TOOLS = [CrosshairTool(), hover]

    # map dataframe indices to date strings and use as label overrides
    p = figure(plot_width=1000, plot_height=700, tools=TOOLS,title = stock+" Candlestick with Custom Date")
    p.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(df["Date"], format='%Y-%m-%d'))
    }
    
    p.yaxis.axis_label = "Price"
    p.xaxis.axis_label = "Date"
    p.grid.grid_line_alpha=0.5

    #this is the up tail 
    r1 = p.segment(df.seq[inc], df.High[inc], df.seq[inc], df.Low[inc], color="green", name='seg_INC')
    #p.add_tools(HoverTool(renderers=[r1], tooltips=[('High', '@y0'), ("Low", "@y1"),]))

    #this is the bottom tail 
    r2 = p.segment(df.seq[dec], df.High[dec], df.seq[dec], df.Low[dec], color="red", name='seg_DEC') 
    #p.add_tools(HoverTool(renderers=[r2], tooltips=[('High', '@y0'), ("Low", "@y1"),]))

    #this is the candle body for the red dates
    p.rect(x='seq', y='mid', width=w, height='height', fill_color="green", name='source_Inc',line_color="green", legend='Close High', source=sourceInc)
    #this is the candle body for the green dates
    p.rect(x='seq', y='mid', width=w, height='height', fill_color="red", name='source_Dec',line_color="red", legend = 'Close Low', source=sourceDec)

    #this is where the ARIMA line
    #p.circle(df.seq, df['Forecast'], color='darkgrey', alpha=0.2, legend='Forecast')
    r3 = p.line(df.seq, df['Forecast'], line_width=2, color='navy', legend='Forecast_line')
    p.add_tools(HoverTool(renderers=[r3], tooltips=[('Forecast', '@y')]))
    
    p.legend.location = "top_left"

    html = file_html(p, CDN, "my plot")

    return html
    
if __name__ == '__main__':
  app.run(host='0.0.0.0') #host='0.0.0.0'



