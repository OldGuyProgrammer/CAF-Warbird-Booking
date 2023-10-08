#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Database Manager
#
#   Jim Olivi 2002
#
import json
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError, OperationFailure
from string import Template
from globals import signals as s, globals as gl, format_time
from datetime import datetime
from flaskmail import FlaskMail


class DatabaseManager:

    def __init__(self, app):

        self.app = app

        db_template = Template(os.getenv('DB_CONNECT_PATH'))
        db_database_name = os.getenv("DB_DATABASE_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_uri = db_template.substitute(USERID=db_user, PASSWORD=db_password, DBNAME=db_database_name)
        app.config['MONGO_URI'] = db_uri
        # print(db_uri)
        try:
            self.dbINDYCAF = PyMongo(app)
        except Exception as e:
            print("Connection failed: ", e)
        else:
            print("Database Initialization Successful")

    def get_person(self, user_id, *args):
        # Only return the specified fields.
        # Functions should not ask for password unless necessary
        if len(args) > 0:
            db_args = {f for f in args}
        else:
            db_args = {}
        try:
            query = {"_id": user_id}
            vol = self.dbINDYCAF.db.volunteers.find_one(query, db_args)
        except OperationFailure as e:
            print(f'Find person failure: {e}')
            return None
        else:
            return vol

    def add_volunteer(self, volunteer_dict):

        try:
            self.dbINDYCAF.db.volunteers.insert_one(volunteer_dict)
        except DuplicateKeyError:
            return s.duplicate_volunteer_id
        except Exception as e:
            print(gl.MSG_ADD_NEW_FAILED, e)
        return s.database_op_success

    # Update Volunteer record according to data passed
    def update_volunteer(self, userid, updates):
        key = {"_id": userid}
        new_stuff = {'$set': updates}
        try:
            self.dbINDYCAF.db.volunteers.update_one(key, new_stuff)
        except Exception as e:
            msg = f"gl.MSG_UPDATE_VOL_FAILED, {e}"
            print(msg)
            return [s.database_op_failure, msg]

        return [s.database_op_success]

    # Retrieve all selected crew member from the database.
    # Convert to a python tuple and return
    def getcrew(self):
        crew_array = []
        try:
            for crew in self.dbINDYCAF.db.volunteers.find({}, {'_id': 1, gl.DB_FIRST_NAME: 1, gl.DB_LAST_NAME: 1}):
                crew_array.append(crew)
        except Exception as e:
            print('getcrew: find op failed', e)

        return crew_array

    # Retrieve all operational airplanes from the database.
    # Convert to a python array and return
    def getairplanes(self):

        fleet_list = []
        try:
            for plane in self.dbINDYCAF.db.aircraft.find({gl.DB_AIRCRAFT_OPERATIONAL: True},
                                                         {"_id": 1,
                                                          gl.DB_AIRCRAFT_NAME: 1,
                                                          gl.DB_AIRCRAFT_IMAGE: 1}):
                # For the Flask form, the second (right most) param is the displayed text...
                # The first (left most) is the value returned.
                airplane_list = [plane["_id"], plane[gl.DB_AIRCRAFT_IMAGE], plane[gl.DB_AIRCRAFT_NAME]]
                fleet_list.append(airplane_list)

        except Exception as e:
            print('getairplanes: find all failed', e)

        return fleet_list

    # Get One aircraft

    def get_one_airplane(self, airplane_id, *args):

        db_args = {f for f in args}

        try:
            plane = self.dbINDYCAF.db.aircraft.find_one({"_id": airplane_id}, db_args)
        except Exception as e:
            print('GetOneAirplane: find failed', e)
            return None
        else:
            return plane

    # Retrieve all flights as requested.
    # Convert to a python array and return
    # Specify dates to search for using startdate and enddate keywords to bracket the dates to search for.
    # Both startdate and enddate must be strings in the format YYYY-mm-dd.
    # If enddate is not requested, the database will be searched for all dates in the future from
    #   the startdate. If no dates are specified, all flights in the future from the current date will be
    #   returned.
    def get_flights(self, *fields, **kwfields):

        db_args = {f for f in fields}
        if "startdate" in kwfields and 'enddate' in kwfields:
            # Find the rides between the two dates

            startdate = datetime.strptime(str(kwfields['startdate']), '%Y-%m-%d')

            # print(f"enddate: {kwfields['enddate']}")
            enddate = datetime.strptime(str(kwfields['enddate']), '%Y-%m-%d')
            if "airportcode" in kwfields:
                query = [
                    {'$match': {
                        'flight_time': {'$gte': startdate, "$lte": enddate},
                        'airport_code': {'$eq': kwfields["airportcode"]}
                    }
                    },
                    {'$lookup': {
                        'from': 'aircraft',
                        'localField': gl.DB_N_NUMBER,
                        'foreignField': '_id',
                        'as': gl.DB_AIRCRAFT_DETAILS
                    }
                    },
                    {
                        "$sort": {gl.DB_FLIGHT_TIME: 1}
                    }
                ]
            else:
                query = [
                    {
                        '$match': {
                            'flight_time': {'$gte': startdate, "$lte": enddate}
                        }
                    }, {
                        '$lookup': {
                            'from': 'aircraft',
                            'localField': gl.DB_N_NUMBER,
                            'foreignField': '_id',
                            'as': gl.DB_AIRCRAFT_DETAILS
                        }
                    }
                ]
        elif "startdate" in kwfields:
            # List all rides after the specified date
            start_date = datetime.strptime(kwfields['startdate'], '%Y-%m-%d')
            query = [
                {'$match': {
                    gl.DB_FLIGHT_TIME: {"$gte": start_date}
                }
                },
                {'$lookup': {
                    'from': 'aircraft',
                    'localField': gl.DB_N_NUMBER,
                    'foreignField': '_id',
                    'as': gl.DB_AIRCRAFT_DETAILS
                }
                },
                {
                    "$sort": {gl.DB_FLIGHT_TIME: 1}
                }
            ]
        else:
            # List all flights
            query = {}

        flight_list = []
        try:
            # Get all flights in the date range, maybe all in the future, sorted ascending
            # If there's a failure, Set up error recovery
            # If success, set error message to empty string.
            flights = self.dbINDYCAF.db.flights.aggregate(query)
            for flight in flights:
                flight["_id"] = str(flight["_id"])
                if gl.DB_FLIGHT_TIME in flight:
                    dt = str(flight[gl.DB_FLIGHT_TIME])
                    flight[gl.DB_FLIGHT_TIME] = dt
                flight_list.append(flight)
        except Exception as e:
            print(gl.MSG_GETFLIGHTS_FAILURE, e)
            flight_list = None
            return [flight_list, e]

        return [flight_list, ""]

    # Get aircraft information from the screen and add to the database
    def AddAircraft(self, new_aircraft):

        try:
            self.dbINDYCAF.db.aircraft.insert_one(new_aircraft)
        except DuplicateKeyError:
            return s.duplicate_aircraft_id
        except Exception as e:
            print("Add_Aircraft_To_Database, insert_one failed: ", e)
            return s.database_op_failure
        else:
            return s.database_op_success

    # Get flight information from the screen.
    def saveFlight(self, flight):

        try:
            flight_id = self.dbINDYCAF.db.flights.insert_one(flight)
            msg = "Flight added to database.\n"
            msg = msg + f"Airport: {flight[gl.DB_AIRPORT_NAME]}\n"
            msg = msg + f"Flight time: {flight[gl.DB_FLIGHT_TIME]}"
            fm = FlaskMail(self.app)
            # fm.send_message("Flight Added", "jimolivi@icloud.com", msg)

            return flight_id
        except Exception as e:
            print("Save Flight, insert_one failed: ", e)
            return None

    # Get one flight record
    def get_one_flight(self, primary_key):
        query = [
            {
                '$match': {
                    '_id': ObjectId(primary_key)
                }
            }, {
                '$lookup': {
                    'from': 'aircraft',
                    'localField': gl.DB_N_NUMBER,
                    'foreignField': '_id',
                    'as': gl.DB_AIRCRAFT_DETAILS
                }
            }
        ]

        try:
            flights = self.dbINDYCAF.db.flights.aggregate(query)
            for flight in flights:
                flight["_id"] = str(flight["_id"])
                flight[gl.DB_FLIGHT_TIME] = flight[gl.DB_FLIGHT_TIME]
                flight[gl.DB_END_FLIGHT_TIME] = flight[gl.DB_END_FLIGHT_TIME]
                new_crew_list = []
                for crew in flight[gl.DB_CREW_LIST]:
                    query = {"_id": crew[gl.DB_COLONEL_NUMBER],}
                    volunteer = self.dbINDYCAF.db.volunteers.find_one(query, {})
                    crew_entry = {
                        gl.DB_COLONEL_NUMBER: crew[gl.DB_COLONEL_NUMBER],
                        gl.DB_FIRST_NAME: volunteer[gl.DB_FIRST_NAME],
                        gl.DB_LAST_NAME: volunteer[gl.DB_LAST_NAME],
                        gl.DB_CREW_POSITION: crew[gl.DB_CREW_POSITION_NAME],
                        gl.DB_ACTIVE: volunteer[gl.DB_ACTIVE]
                    }
                    new_crew_list.append(crew_entry)
                flight[gl.DB_CREW_LIST] = new_crew_list
                return flight
        except Exception as e:
            msg = 'Find One Flight: ' + gl.MSG_FIND_OP_FAILED
            print(msg)
            raise Exception(msg)

        return None

    # Update Flight Record
    def update_flight(self, flight_id, updates):

        flight_id = ObjectId(flight_id)
        try:
            self.dbINDYCAF.db.flights.update_one({"_id": flight_id}, {'$set': updates})
        except Exception as e:
            print(gl.MSG_UPDATE_FLIGHT_FAILED, e)
            return s.database_op_failure

        return s.database_op_success

    # Update Flight Record, add array elements.
    def updateFlightArray(self, flight_id, updates):

        flight_id = ObjectId(flight_id)
        try:
            self.dbINDYCAF.db.flights.update_one({"_id": flight_id}, {'$addToSet': updates})
        except Exception as e:
            print(gl.MSG_UPDATE_FLIGHT_FAILED, e)
            return s.database_op_failure

        return s.database_op_success
