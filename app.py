# Import everything you used in the starter_climate_analysis.ipynb file, along with Flask modules
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
# Create an engine
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect an existing database into a new model with automap_base() and Base.prepare()
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Instantiate a Session and bind it to the engine
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Instantiate a Flask object at __name__, and save it to a variable called app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Set the app.route() decorator for the base '/'
# define a welcome() function that returns a multiline string message to anyone who visits the route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2016-08-23/2017-08-23      First and last date <br/>"
        f"/api/v1.0/temp/2016-08-23      First date"
    )
        

# Set the app.route() decorator for the "/api/v1.0/precipitation" route
# define a precipitation() function that returns jsonified precipitation data from the database
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date 1 year ago from last date in database
    last_date = (session
        .query(Measurement.date)
        .order_by(Measurement.date.desc())
        .first().date)

    query_dates = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    # Create a dictionary to store the date: prcp pairs. 
    # Hint: check out a dictionary comprehension, which is similar to a list comprehension but allows you to create dictionaries
    precipitation_data = (session
        .query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= query_dates)
        .all()
    )

    prcp_pairs = []
    for prcp in precipitation_data:
        prcp_dict = {}
        prcp_dict['date'] = prcp[0]
        prcp_dict['prcp'] = prcp[1]
        prcp_pairs.append(prcp_dict)


    # close session
    session.close()

    # Return the jsonify() representation of the dictionary
    return jsonify(prcp_pairs)

# Set the app.route() decorator for the "/api/v1.0/stations" route
# define a stations() function that returns jsonified station data from the database
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)  
    # Query for the list of stations
    station_list = (session
        .query(Station.station)
        .all()
    )
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    tations_ravel = list(np.ravel(station_list, order='F'))

    # close session
    session.close()

    # Return the jsonify() representation of the list
    return jsonify(tations_ravel)


# Set the app.route() decorator for the "/api/v1.0/tobs" route
# define a temp_monthly() function that returns jsonified temperature observations (tobs) data from the database
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from last date in database
    last_date = (session
        .query(Measurement.date)
        .order_by(Measurement.date.desc())
        .first().date)

    query_dates = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    tobs = (session
     .query(Measurement.date, Measurement.station, Measurement.tobs)
     .filter(Measurement.date >= query_dates)
     .filter(Measurement.station == 'USC00519281')
     .all())
    
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    tobs_ravel = list(np.ravel(tobs))

    # close session
    session.close()

    # Return the jsonify() representation of the list
    return jsonify(tobs_ravel)


# Set the app.route() decorator for the "/api/v1.0/temp/<start>" route and "/api/v1.0/temp/<start>/<end>" route
# define a stats() function that takes a start and end argument, and returns jsonified TMIN, TAVG, TMAX data from the database
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    last_date = (session
        .query(Measurement.date)
        .order_by(Measurement.date.desc())
        .first().date)

    query_dates = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    if end != None:
        # calculate TMIN, TAVG, TMAX for dates both start and stop 
        tempature_avg = (session
        .query(func.max(Measurement.tobs).label('Highest tempature'), func.min(Measurement.tobs).label('Lowest tempature'), func.avg(Measurement.tobs).label('Average tempature'))
        .filter(Measurement.station == 'USC00519281')
        .filter(Measurement.date >= start, Measurement.date <= end)
        .all())

        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        temp_ravel = list(np.ravel(tempature_avg))

        # close session
        session.close()
        # Return the jsonify() representation of the list
        return jsonify(temp_ravel)

    else:
        # calculate TMIN, TAVG, TMAX with greater than start
        tempature_avg_else = (session
        .query(func.max(Measurement.tobs).label('Highest tempature'), func.min(Measurement.tobs).label('Lowest tempature'), func.avg(Measurement.tobs).label('Average tempature'))
        .filter(Measurement.station == 'USC00519281')
        .filter(Measurement.date >= start)
        .all())
        
        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        temp_ravel_else = list(np.ravel(tempature_avg_else))

        # close session
        session.close()

        # Return the jsonify() representation of the list
        return jsonify(temp_ravel_else)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
