from flask import Flask, render_template, request, redirect
import requests as rq

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/view_ticker', method=['GET', 'POST'])
def view_ticker():
    stock = rq.form['ticker']
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock 
    session = rq.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    return raw

if __name__ == '__main__':
  app.run(host='0.0.0.0')
