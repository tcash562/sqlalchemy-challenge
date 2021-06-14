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

# View all of the classes that automap found
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate App!<br/>"

        f"Available Routes:<br/>"
        f"Preciptitaion - /api/v1.0/precipitation<br/>"
        f"Stations - /api/v1.0/stations<br/>"
        f"Temperature Observations - /api/v1.0/tobs<br/>"
        f"Start Date - /api/v1.0/start<br/>"
        f"End Date - /api/v1.0/start/end"
        )

# Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all dates and prcp for last year
    results = session.query(Measurement.date).all()
    all_results = session.query(Measurement.date).order_by(Measurement.date.desc()).all()

    year_results = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').group_by(Measurement.date).all()

    session.close()

    prcp_results = []

    for date, prcp in year_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        prcp_results.append(precipitation_dict)

    return jsonify(prcp_results)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    tobs_year_results = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= '2016-08-23').group_by(Measurement.date).all()


    session.close()

    tobs_results = []

    for date, tobs in tobs_year_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start = session.query(func.min(Measurement.date)).first()[0]

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).\
    filter(Measurement.date >= "start").all()

    session.close()

    temp_date = list(np.ravel(results))
    return jsonify(temp_date)

@app.route("/api/v1.0/<start>/<end>")
def end(start=None, end=None):
    session = Session(engine)

    start = session.query(func.min(Measurement.date)).first()[0]
    end = session.query(func.min(Measurement.date)).last()[0]

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).\
    filter(Measurement.date >= "start").\
    filter(Measurement.date >= "end").all()

    session.close()

    end_date = list(np.ravel(results))
    return jsonify(end_date)

if __name__ == "__main__":
    app.run(debug=True)
