import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

def date_calc():

    latest_date = session.query(func.max(Measurement.date)).all()

    session.close
   
    today = dt.date.today()
    lastest_date_datefmt = today.replace(year=int(latest_date[0][0][:4]),\
                                        month=int(latest_date[0][0][5:7]),\
                                        day=int(latest_date[0][0][8:]))
    
    one_year_backdate = lastest_date_datefmt-dt.timedelta(days=365)
    
    data_end_date_ymd = lastest_date_datefmt.strftime("%Y-%m-%d")
    start_date_ymd = one_year_backdate.strftime("%Y-%m-%d")
    
    Year_list = [start_date_ymd,data_end_date_ymd]
    return(tuple(Year_list))

app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page")
    return f"""Available Routes:<br/>
        <br/>
        /api/v1.0/precipitation<br/>
        <br/>
        /api/v1.0/stations<br/>
        <br/>
        /api/v1.0/tobs<br/>
        <br/>
        /api/v1.0/start<br/>
        <br/>
        /api/v1.0/start/end<br/>
        <br/>
        Note:
        Latest available date is 2017-08-23
        start and end dates must be in 'YYYY-MM-DD' format"""
    

@app.route("/api/v1.0/precipitation")
def percipitation():
    print("Server received request for 'Precipitation' page")

    range = date_calc()
    end_date = range[1]
    start_date = range[0]
        
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
        filter(Measurement.date <= end_date).\
        filter(Measurement.date >= start_date).all()
        
    session.close
         
    all_percipitation = []
    for result in results:
        percipitation_dict = {"Date":result[0], "Station":result[1],"Precipitation":result[2]}
        all_percipitation.append(percipitation_dict)
    
    return jsonify(all_percipitation)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Station' page")
        
    results = session.query(Station.station, Station.name).all()
        
    session.close

    all_stations = []
    for result in results:
        stations_dict = {"Station ID:":results[0],"Station Name":results[1]}
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'TOBS' page")

    Range = date_calc()
    End_date = Range[1]
    Start_date = Range[0]
        
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date <= End_date).\
        filter(Measurement.date >= Start_date).\
        filter(Measurement.station == 'USC00519397').all()
        
    session.close

    all_tobs = []
    for temp in results:
        stations_dict = {"Date": temp[0], "Temperature": temp[1]}
        all_tobs.append(stations_dict)
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def timestart(start):
        
    print("Server received request for 'Starting Weather Date' page")
        
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close
    
    results_dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1], "Maximum Temp":results[0][2]}

    return jsonify(results_dict)
    
@app.route("/api/v1.0/<start>/<end>")
def timestartend(start,end):
    print("Server received request for 'Weather Date Range' page")

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close
    
    results_dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1], "Maximum Temp":results[0][2]}

    return jsonify(results_dict)

if __name__ == '__main__':
    app.run(debug=True)