from flask import Flask, render_template, request, redirect
import requests as rq
import quandl as qd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, HoverTool,CrosshairTool
from bokeh.core.properties import value
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from datetime import datetime
import pandas as pd
import numpy as np
#we dont need this "from pandas_datareader.data import DataReader"
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
#calculating business day
from pandas.tseries.offsets import BDay
from statsmodels import api as sm 
from flask import render_template

#test

app = Flask(__name__)

#this is the general 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock_predict', methods=['GET', 'POST'])
def stock_predict():
    # having a default start date that is 3 months ago
    start = date.today() - relativedelta(months=+3)
    #pd.offsets.BDay(1) is for having a date before start date (this is for the volume histogram)
    start = start - pd.offsets.BDay(1)
    end = date.today()
    return render_template('stock_predict.html', start=str(start), end=str(end))

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

    #this is the checking for server error message
    if start > end:
	return 'Invalid end date. Please select end date not in future.'

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
     
    #Yahoo Actions has been immediately deprecated due to large breaks in the API without the introduction of a stable replacement.
    #df = DataReader(stock, 'yahoo', start, end)
    
    df = qd.get("WIKI/" + stock, start_date=start, end_date=end, api_key='oSvidbxNa84mVv7Kzqh2')
    #df = qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')

    
    df.reset_index(inplace=True,drop=False)

    #This is where ARIMA starts
    df['Natural Log'] = df['Close'].apply(lambda x: np.log(x))
    price_matrix = df['Close'].as_matrix()
    model = sm.tsa.ARIMA(price_matrix, order=(1, 0, 3))
    results = model.fit(disp=-1) #disp=1 (disp < 0 means no output in this case. 1 = output)
    #df['Forecast'] = results.fittedvalues

    #Add one more day
    df['Date']=pd.to_datetime(df['Date'])
    end_new = end + pd.offsets.BDay(1)
    df = df.append ({'Date':end_new}, ignore_index=True)


    df['changepercent'] = df.Close.pct_change()*100
    seqs=np.arange(df.shape[0]) 
    df["seq"]=pd.Series(seqs)
    df["Date"] = pd.to_datetime(df["Date"])
    df['Date']=df['Date'].apply(lambda x: x.strftime('%Y/%m/%d'))
    df['changepercent']=df['changepercent'].apply(lambda x: str(round(x,2))+"%")
    df['mid']=df.apply(lambda x:(x['Open']+x['Close'])/2,axis=1)
    df['height']=df.apply(lambda x:abs(x['Close']-x['Open'] if x['Close']!=x['Open'] else 0.001),axis=1)
    
    #Use () and | to fix no candlestick graph show when close and open price is the same per that date
    inc = (df.Close > df.Open) | (df.Close == df.Open)
    dec = (df.Open > df.Close) | (df.Open == df.Close)
    w=0.5


    #Calculation for volume graph
    close_inc = (df.Close.diff() > 0)
    close_dec = (df.Close.diff() < 0)
    df['volinc'] = df.Volume[close_inc]
    df['voldec'] = df.Volume[close_dec]


    #filter the first row of the dataframe so volume histogram can show
    df=df.iloc[1:]
    print df

    #Add additional Forecast Day
    forecast_start = df.index[0]
    forecast_end = df.index[-1]
    #print forecast_start
    #print forecast_end

    #forcast = results.predict(forecast_start, forecast_end, dynamic=False) #, dynamic= True means in-sample
    df['Forcast_New']=results.predict(forecast_start, forecast_end, dynamic=False)
    #print df

    # print df.iloc[-3:]
    #forecast= results.predict(start, end, dynamic=True)
    # print forecast

    #use ColumnDataSource to pass in data for tooltips
    sourceInc=ColumnDataSource(ColumnDataSource.from_df(df.loc[inc]))
    sourceDec=ColumnDataSource(ColumnDataSource.from_df(df.loc[dec])) 
    sourceAll=ColumnDataSource(ColumnDataSource.from_df(df.loc[:]))   
    #will not need this one because we are putting a separate hoover to the forecast line
    #sourceforecast=ColumnDataSource(ColumnDataSource.from_df(df.loc[:]))


    #the values for the tooltip come from ColumnDataSource
    hover = HoverTool(
        names=['source_Inc', 'source_Dec', 'volinc', 'voldec'],
        tooltips=[
            ("Date", "@Date"),
            ("Open", "@Open"),
            ("Close", "@Close"),
            ("High", "@High"),
            ("Low", "@Low"),
	    ("Volume", "@Volume"),
            ("Percent", "@changepercent"),
           # ("Forecast", "@Forecast"),
        ]
    )

    TOOLS = [CrosshairTool(), hover]

    # map dataframe indices to date strings and use as label overrides
    p = figure(plot_width=900, plot_height=500, tools=TOOLS,title = stock+" Candlestick with Custom Date")
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
    r3 = p.line(x='seq', y='Forcast_New', line_width=2, color='navy', legend='Forecast_line', source=sourceAll)
    p.add_tools(HoverTool(renderers=[r3], tooltips=[('Date', '@Date'),('Forecast', '@Forcast_New')]))

    #r4 = p.line(df.seq, df['Forecast2'], line_width=2, color='yellow', legend='Future_Day1')
    #p.add_tools(HoverTool(renderers=[r4], tooltips=[('Forecast', '@y')]))

    
    p.legend.location = "top_left"

    #This is the histogram graph
    p2 = figure(width=p.plot_width, x_range=p.x_range, tools=TOOLS, height=150, title='Volume')
    p2.vbar(x='seq', top='volinc', width=1, bottom=0, color="green", source=sourceAll, name='volinc')
    p2.vbar(x='seq', top='voldec', width=1, bottom=0, color="red", source=sourceAll, name='voldec')

    p_all=(column(p, p2))


    html = file_html(p_all, CDN, "my plot")

    return html
    
if __name__ == '__main__':
  app.run() #host='0.0.0.0' debug=True




