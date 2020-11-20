from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    apis = [
        {
            'serial': 1,
            'exchange': 'binance',
            'public_key': 'adfadsfsfdgasdfdsafasedf',
            'secret_key': 'asdgfregasdfsadfdsfrqgetgjnuyitu',
            'date_added': '10 Jun 2010',
        },
        {
            'serial': 2,
            'exchange': 'bittrex',
            'public_key': 'adfadsfsfdgasdfdsafasedf',
            'secret_key': 'asdgfregasdfsadfdsfrqgetgjnuyitu',
            'date_added': '11 Jun 2010',
        }
    ]
    scanners = [
        {
            'serial': 1,
            'status': 'started',
            'name': 'scanner 1',
            'exchange': 'binance',
            'interval': '5 min',
            'config_desc': 'this is a test config 21234',
        },
        {
            'serial': 2,
            'status': 'stopped',
            'name': 'scanner 2',
            'exchange': 'gemini',
            'interval': '15 min',
            'config_desc': 'this is a test config sadfhahsdfhasdhfsdhfh',
        }
    ]
    return render_template('index.html', apis=apis, scanners=scanners)


@app.route('/add_scanner')
def add_scanner():
    exchanges = ['binance', 'gemini']
    return render_template('add_scanner.html', exchanges=exchanges)


@app.route('/add_api')
def add_api():

    return render_template('add_api.html')


@app.route('/scanner/<int:scanner_serial>')
def open_scan(scanner_serial):

    return render_template('scanner.html', scanner_serial=scanner_serial)