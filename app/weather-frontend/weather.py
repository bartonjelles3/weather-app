import flask
import requests
import json
import prometheus_client
import logging

application = flask.Flask(__name__)

duration = prometheus_client.Summary('request_processing_seconds',
                                    'Time spent processing weather request')

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
    logging.info(f'Sending request to http://weather-query-svc.default.svc.cluster.local:8081/weather_query')
    
    try:
        response = requests.post("http://weather-query-svc.default.svc.cluster.local:8081/weather_query",
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

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=8080)
