# Flask modules
from flask import render_template, request
from app import app

# Python modules
import pandas as pd

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


@app.route('/add_scanner', methods=['POST', 'GET'])
def add_scanner():
    if request.method == 'POST':
        form_data = request.form
        scanner_name = form_data['inputName']
        scanner_exchange = form_data['inputExchange']
        scanner_interval = form_data['inputInterval']
        
        prefilter_quantity = {k[-1]:v for k,v in form_data.items() if 'quantity' in k}
        prefilter_condition = {k[-1]:v for k,v in form_data.items() if 'condition' in k}
        prefilter_value = {k[-1]:v for k,v in form_data.items() if 'value' in k}
        prefilter_lookback = {k[-1]:v for k,v in form_data.items() if 'lookback' in k}

        prefilter_datatable = pd.DataFrame(columns=[''])
        prefilters_data = {prefilter_data[k[-1]][k[:-1]]:1 for k,v in form_data.items() if k[-1].isdigit()}
        # prefilters_data = {k[-1]:{k[:-1]:v} for k,v in form_data.items() if k[-1].isdigit()}

        print(form_data)
        print(scanner_name)
        print(prefilters_data)
    else:
        exchanges = ['binance', 'gemini']
        return render_template('add_scanner.html', exchanges=exchanges)


@app.route('/add_api', methods=['POST', 'GET'])
def add_api():
    if request.method == 'POST':
        print(request.form)
    else:
        return render_template('add_api.html')


@app.route('/scanner/<int:scanner_serial>')
def open_scan(scanner_serial):

    return render_template('scanner.html', scanner_serial=scanner_serial)