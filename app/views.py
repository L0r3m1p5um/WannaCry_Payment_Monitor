from app import app
from flask import render_template
from wannacrymonitor import WannacryMonitor
import threading
import locale

monitor = WannacryMonitor()
locale.setlocale(locale.LC_ALL, '')

@app.route('/')
def index():
    return render_template('index.html',monitor=monitor)
        