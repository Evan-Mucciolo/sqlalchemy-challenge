# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Declare a Base using `automap_base()`
base = automap_base()

# Use the Base class to reflect the database tables
base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
measurement = base.classes.measurement

station = base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
        return(f"Welcome<br>"
               f"Available Routes:<br>"
               f"/api/v1.0/precipitation<br>"
               f"/api/v1.0/stations<br>"
               f"/api/v1.0/tobs<br>"
               f"/api/v1.0/<start> (Enter date as mm-dd-yyy) <br>"
               f"/api/v1.0/<start>/<end> (Enter start date/end date as mm-dd-yyy)"               
               
               )  
    
        
    
@app.route('/api/v1.0/precipitation')
def precipitation():
        # Create a session
        session = Session(engine)

        # Find the most recent date in the data set.
        most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
        
        # Design a query to retrieve the last 12 months of precipitation data and plot the results.
        # Starting from the most recent data point in the database.
        starting_date = dt.datetime.strptime(most_recent_date[0], "%Y-%m-%d")


        # Calculate the date one year from the last date in data set.
        query_date = starting_date - dt.timedelta(days=366)

        # Perform a query to retrieve the data and precipitation scores
        query = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).all()
        
        session.close()

        # Create an empty list
        prcp_list = []
        
        for date, prcp in query:
                # Convert to a dictionary
                prcp_dict = {}
                prcp_dict["Date"] = date
                prcp_dict["Precipitation"] = prcp
                prcp_list.append(prcp_dict)
        
        return jsonify(prcp_list)

@app.route('/api/v1.0/stations')
def stations():
        # Return a JSON list of stations from the dataset
        
        session = Session(engine)
        
        stations = session.query(measurement.station).\
            group_by(measurement.station).all()
        
        session.close()
        
        station_list = []
        
        for station in stations:
                station_list.append(station[0])
        
        return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
        session = Session(engine)
        
        temps = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station == 'USC00519281').all()
        
        session.close()
        
        # Create an empty list
        tobs_list = []
        
        for date, tobs in temps:
                # Convert to a dictionary
                tobs_dict = {}
                tobs_dict["Date"] = date
                tobs_dict["Observed_Temperature"] = tobs
                tobs_list.append(tobs_dict)
        
        
        return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
        
        try:
                date_entered = dt.datetime.strptime(start, "%m-%d-%Y")
        except:
                return f"Please Enter the date in mm-dd-yyyy format."
        
        
        # Start session
        session = Session(engine)
        
        # Run Query
        query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= date_entered).all()      
        
        
        # Check to see if query result is not empty
        
        if query:
                temps_list = []      
                # Create a dictionary
                tobs_dict = {}
                tobs_dict["TMIN"] = query[0][0]
                tobs_dict["TAVG"] = query[0][2]
                tobs_dict["TMAX"] = query[0][1]
                
                temps_list.append(tobs_dict)          
                
        
        return (jsonify(temps_list))

@app.route('/api/v1.0/<start>/<end>')
def end(start,end):
        
        try:
                start_date_entered = dt.datetime.strptime(start, "%m-%d-%Y")
                end_date_entered = dt.datetime.strptime(end, "%m-%d-%Y")
        except:
                return f"Please Enter the date in mm-dd-yyyy format."
        
        
        # Start session
        session = Session(engine)
        
        # Run Query
        query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date_entered, measurement.date <= end_date_entered).all()      
        
        
        # Check to see if query result is not empty
        
        if query:
                temps_list = []      
                # Create a dictionary
                tobs_dict = {}
                tobs_dict["TMIN"] = query[0][0]
                tobs_dict["TAVG"] = query[0][2]
                tobs_dict["TMAX"] = query[0][1]
                
                temps_list.append(tobs_dict)          
                
        
        return (jsonify(temps_list))

if __name__ == "__main__":
    app.run(debug=True)