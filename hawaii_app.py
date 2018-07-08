
from flask import Flask
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


engine = create_engine("sqlite:///hawaii.db")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Save paths to the tables in the Hawii DB
Measurements = Base.classes.measurements
Stations = Base.classes.stations

# Create a session (link) from Python to the Hawaii DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    print('received request for home page')
    return(
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
    )

@app.route("/api/v1.0/precipitation")
# Query for the dates and temperature observations from the last year
def precipitation():
    print("Server received request for 'prcp' page")
    
    results = session.query(Measurements.prcp, Measurements.date).filter(Measurements.date.between('2016-01-01', '2016-12-31')).all()

    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    print("server request received for Stations")

    results = session.query(Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation).all()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
# Return a JSON list of Temperature Observations (tobs) for the previous year
def temperature():
    print("server request received for Stations")

    sel = [Measurements.tobs, Measurements.date]

    results = session.query(*sel).filter(Measurements.date.between('2016-01-01', '2016-12-31')).all()

    return jsonify(results)

@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

def weather_start(start):  
    print("server request received for weather_start")

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    sel = [func.max(Measurements.tobs).label('Max'), func.min(Measurements.tobs).label('Min'),func.avg(Measurements.tobs).label('average')]
    
    results = session.query(*sel).filter(Measurements.date >= start).all()  
    
    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def weather_span_date(start,end): 
    print("server request eceived for weather_span_date")
    
    start_date = dt.datetime.strptime(start,'%Y-%m-%d' )
    end_date = dt.datetime.strptime(end,'%Y-%m-%d' )

    sel = [func.max(Measurements.tobs).label('Max'), func.min(Measurements.tobs).label('Min'),func.avg(Measurements.tobs).label('average')]
    
    results = session.query(*sel).filter(Measurements.date.between(start_date, end_date)).all()

    results = list(np.ravel(results))

    return jsonify(results)



if __name__ == "__main__":
    app.run(debug=True)