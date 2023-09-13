from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return  render_template("index.html")
@app.route('/-th')
def index_th():
    return render_template('index_th.html')
def help():
    app.run()
