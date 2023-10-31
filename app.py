# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
# engine = create_engine("sqlite:///Users/vdumlao/Documents/GitHub/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
# Base.classes.keys()

# Save references to each table
Measurements = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
recent_dateset = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
recent_date = recent_dateset.date
prior_one_year = dt.datetime.strptime(recent_date,'%Y-%m-%d') - dt.timedelta(days=366)
active_stations = session.query(Measurements.station,func.count(Measurements.station)).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc()).all()
most_active = active_stations[0][0]
active_caluc = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).\
    filter(Measurements.station == most_active).all()
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
        f"Welcome to Hawaii Weather Stations API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation_scores = session.query(Measurements.date,Measurements.prcp).filter(Measurements.date >= prior_one_year).all()

    prcp_list = []
    for date, prcp in prcp_list:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
    

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Measurements.station).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc()).all()
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperature():
    temperature_active = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.station == most_active).\
        filter(Measurements.date >= prior_one_year).\
        group_by(Measurements.date).all()
    
    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def start():
    start_date = session.query(func.min(Measurements.tobs),func.avg(Measurements.tobs),func.max(Measurements.tobs)).\
        filter(Measurements.date == prior_one_year).all()
    
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    startend_date = session.query(func.min(Measurements.tobs),func.avg(Measurements.tobs),func.max(Measurements.tobs)).\
        filter(Measurements.date >= prior_one_year).all()
    return jsonify(startend_date)

if __name__ == '__main__':
    app.run(debug=True)