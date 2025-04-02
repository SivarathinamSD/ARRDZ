from flask import Flask, render_template, redirect, request, session
import requests
from flask_session import Session
import datetime

BASE_API = "https://roverdata2-production.up.railway.app"
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False   
app.config["SESSION_TYPE"] = "filesystem"     
app.secret_key = 'SECRET KEY'
Session(app)

def start_session():
    response = requests.post(f"{BASE_API}/api/session/start")
    print(response)
    data = response.json()
    return data.get("session_id")

def time_conversion(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return ([dt_object.strftime("%d-%b-%Y"), dt_object.strftime("%X")] )


def movements(direction):
    print("i worked")
    response = requests.post(f"{BASE_API}/api/rover/move?session_id={session['id']}&direction={direction}")
    #print(f"{BASE_API}/api/rover/move?session_id={session}&direction={direction}")
    data = response.json()
    return data.get("message")

def charge():
    response = requests.post(f"{BASE_API}/api/rover/charge?session_id={session['id']}")
    data = response.json()
    return data.get("message")



@app.route("/", methods =["GET", "POST"])
def index():
    
    if not session.get("id"):
        session["id"] = start_session()
         
        return redirect("/")
    rover_data = requests.get(f"{BASE_API}/api/rover/status?session_id={session['id']}")
    rover_status = rover_data.json()

    if(rover_status['battery'] < 20):
        charge()
    

    if request.method == 'POST':
        if 'up' in request.form:
            action = "forward"
        elif 'left' in request.form:
            action = "left"
        elif 'right' in request.form:
            action = "right"
        elif 'down' in request.form:
            action = "backward"
        else:
            action = "No button clicked"
        print("actions", action)
        print(movements(action))
    

    rover_data = requests.get(f"{BASE_API}/api/rover/status?session_id={session['id']}")
    rover_status = rover_data.json()

    sensor = requests.get(f"{BASE_API}/api/rover/sensor-data?session_id={session['id']}")
    sensor_data = sensor.json()

    # print(sensor_data, rover_status)
    #print(sensor_data)
    timestamp = time_conversion(sensor_data['timestamp'])
    
    
    return render_template("index.html", timestamp = timestamp, sensor_data = sensor_data, rover_status = rover_status)

if __name__ == '__main__':
    app.run(debug=True)