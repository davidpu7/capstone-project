f <li><a target="_blank" href="https://www.heroku.com/">Heroku</a></li>
            <li><a target="_blank" href="http://flask.pocoo.org/">Flask</a></li>
            <li><a target="_blank" href="http://jinja.pocoo.org/docs/2.9/">Jinja2</a></li>
            <tstrap</a></li>rom flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

if __name__ == '__main__':
  app.run(port=33507)
