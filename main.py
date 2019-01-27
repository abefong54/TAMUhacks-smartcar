import smartcar
import os
import logging
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
from flask_ask import Ask, statement, question, session
import json

CLIENT_ID = 'e2130b98-749c-451e-b7e9-299c92c49cff'
CLIENT_SECRET = '49eccd13-150f-4466-844f-f51320fef8b8'
REDIRECT_URI = 'http://localhost:8000/exchange'
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


app = Flask(__name__)
ask = Ask(app, "/")

CORS(app)


# global variables
access = None
miles_until_oil_change=5000

client = smartcar.AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=['read_vehicle_info', 'read_odometer'],
    test_mode=True,
)

@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    return redirect(auth_url)


@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')
    # access our global variable and store our access tokens
    global access
    print("Code: ", code)
    access = client.exchange_code(code)
    return redirect('http://localhost:8000/vehicle')

@ask.launch
@ask.intent("GetCarInfoIntent")
@app.route('/vehicle', methods=['GET'])
def vehicle():

    global access
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    info = vehicle.info()
    odometer = vehicle.odometer()
    carName = info['make'] + " " + info['model']
    kilometers = odometer['data']['distance']
    mileage = kilometers * 0.62137
    save_mileage_to_db(mileage)


    values ={
            'name':carName,
            'currentmileage':mileage,
            'oldmileage':get_old_mileage(),
            'needs_oil_change': True if (mileage - get_old_mileage() > miles_until_oil_change) else False,
        }

    return jsonify(values)#
    pass


def save_mileage_to_db(mileage):
    global miles_until_oil_change
    with open('data.json') as f:
        data = json.load(f)
        oldMiles= int(data["old_mileage"])

        if oldMiles < mileage:
            if(oldMiles - miles_until_oil_change):
                print("NEED OIL CHANGE!")

            data["old_mileage"] = str(mileage)

            print("mileage updated")

def get_old_mileage():
    with open('data.json') as f:
        data = json.load(f)
        return int(data["old_mileage"])


if __name__ == '__main__':
    # save_mileage_to_db(4100000)
    # exit()
    app.run(port=8000, debug=True)
    # print(get_vehicle_info())



