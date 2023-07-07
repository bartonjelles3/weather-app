'Queries OpenWeatherMap for current temperature based on ZIP'

import logging

from owm_key import API_KEY

import flask
import requests
import prometheus_client

application = flask.Flask(__name__)

coord_requests = prometheus_client.Counter("owm_coord_requests", 
                                           'Requests to OWM for lat, lon')
temp_requests = prometheus_client.Counter('owm_temp_requests',
                                          'Requests to OWM for temp')

logging.basicConfig(level=logging.INFO)

@application.route('/weather_query', methods=['POST'])
def weather_query():
    'Takes ZIP, queries OWM for latitude, longitude to request current temp in location.'
    req = flask.request.get_json()
    req_zip = req['zip']
    logging.info('Got request, processing.')
    try:
        location_resp = requests.get(f'http://api.openweathermap.org/geo/1.0/zip?zip={req_zip},US&appid={API_KEY}')
        coord_requests.inc()
        location_resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    lat, lon = location_resp.json()['lat'], location_resp.json()['lon']
    logging.info(f"Got {lat}, {lon}")

    try:
        weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={API_KEY}')
        temp_requests.inc()
        weather_resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
    temp = weather_resp.json()['main']['temp']
    return flask.jsonify({'temperature': temp})

@application.route('/metrics')
def metrics():
    return prometheus_client.generate_latest()

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=80)

