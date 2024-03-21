# Import Dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def home():
    return (
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    last_year = dt.date(2017,8,23,)-dt.timedelta(days=365)
    data_year = session.query(measurement.date, measurement.prcp).where(measurement.date >= last_year)
    
    session.close()

    last_year_df = pd.DataFrame(data_year, columns=["date", "precipitation"]).sort_values("date", ascending=True).dropna()
    dict_prcp = last_year_df.groupby('date')['precipitation'].apply(list).to_dict()
    return jsonify(dict_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(station.station).all()
    
    session.close()
    
    station_list = list(np.ravel(station_list))
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_year = dt.date(2017,8,23,)-dt.timedelta(days=365)
    temp_data = session.query(measurement.date, measurement.tobs).where(measurement.date >= last_year).\
        where(measurement.station == "USC00519281").all()

    session.close()

    temp_df = pd.DataFrame(temp_data, columns=["date", "temp"]).sort_values("date", ascending=True).dropna()
    dict_temp = temp_df.groupby('date')['temp'].apply(list).to_dict()
    return jsonify(dict_temp)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    temp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    where(measurement.date >= start).all()

    session.close()

    start_range = list(np.ravel(temp_data))
    return jsonify(start_range)


@app.route("/api/v1.0/<start>/<end>")
def strtend(start, end):
    session = Session(engine)
    temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    where(measurement.date >= start).where(measurement.date <= end).all()

    session.close()

    range_temps = list(np.ravel(temps))
    return jsonify(range_temps)


if __name__ == '__main__':
    app.run(debug=True)