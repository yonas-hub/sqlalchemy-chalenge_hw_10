import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all station
    results = session.query(Station).all()
    print (results)
    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for stationvar in results:
        station_dict = {}
        station_dict["station"] = stationvar.station
        all_stations.append(station_dict)
    return jsonify(all_stations)
@app.route("/api/v1.0/tobs")
def tobs():
    date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    results=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()
    # create a dictionary for dates and temperature observations from a year from the last data point
    all_data = []
    for tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = tobs.date
        tobs_dict["tobs"]=tobs.tobs
        all_data.append(tobs_dict)
    return jsonify(all_data)
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp(start=None,end=None):
    tempdata=[func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    if not end:
        result = session.query(*tempdata).\
            filter(Measurement.date>=start).all()
        templist=list(np.ravel(result))
        return jsonify(templist) 
    # calculate TMIN, TAVG, TMAX with start and stop
    result = session.query(*tempdata).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    templist = list(np.ravel(result))
    return jsonify(templist)
if __name__ == '__main__':
    app.run(port=5001)