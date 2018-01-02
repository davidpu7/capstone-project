from flask import Flask, render_template, request, redirect
import requests as rq
import quandl as qd

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/view_ticker', methods=['GET', 'POST'])
def view_ticker():
    stock = request.form['ticker']
    value = 0.4

    if 'close' in request.form:
        value = 0.4
    if 'adj_close' in request.form:
        value = 0.10
    if 'open' in request.form:
        value = 0.1
    if 'adj_open' in request.form:
        value = 0.7

    mydata =  qd.get("WIKI/" + stock + value, rows = 20, api_key='oSvidbxNa84mVv7Kzqh2')
    html = file_html(mydata)
    return html

if __name__ == '__main__':
  app.run(host='0.0.0.0')
