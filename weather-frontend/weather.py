import flask
import requests
import json
import prometheus_client
import logging
import os

application = flask.Flask(__name__)

duration = prometheus_client.Summary('request_processing_seconds',
                                    'Time spent processing weather request')

query_svc_addr = os.environ["QUERY_SVC_ADDR"]
weather_query_addr = query_svc_addr + '/weather_query'

logging.basicConfig(level=logging.INFO)

@application.route('/')
def home():
    'Weather homepage.'
    return flask.render_template('home.html')

@duration.time()
@application.route('/get_weather', methods=['GET'])
def get_weather():
    'Gets the weather via an API call to a backend that queries OpenWeatherMap.'
    data = {'zip': flask.request.args.get('zip')}
    headers = {'Content-Type': 'application/json'}
    logging.info(f'Sending request to {weather_query_addr}')
    
    try:
        response = requests.get(weather_query_addr,
                                 data=json.dumps(data), headers=headers)
        response.raise_for_status() 
        
        return flask.render_template('home.html', temperature=int(response.json()['temperature']))
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error connecting to the backend: {str(e)}')
        error_message = 'Error: Query service is currently unavailable.'
        
        return flask.render_template('home.html', error_message=error_message), 500

@application.route('/metrics')
def metrics():
    return prometheus_client.generate_latest()

@application.route('/readyz')
def readyz():
    try:
        weather_resp = requests.get(f'{query_svc_addr}/readyz')
        weather_resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        flask.abort(503)
    return flask.Response('Weather frontend: good', status=200)

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=80, debug=True)
