#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Database Manager
#
#   Jim Olivi 2002
#

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

    def get_person(self, user_id, args):
        # Only return the specified fields.
        # Functions should not ask for password unless necessary
        db_args = {f for f in args}
        try:
            query = {"_id": user_id}
            vol = self.dbINDYCAF.db.volunteers.find_one(query, db_args)
            if vol is not None:
                vol[gl.DB_RECORD_KEY] = vol.pop("_id")
        except OperationFailure as e:
            print(f'Find person failure: {e}')
            return None
        else:
            return vol

    def add_volunteer(self, volunteer_dict):

        volunteer_dict["_id"] = volunteer_dict.pop(gl.DB_RECORD_KEY)
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
    def getcrew(self, crew_select):
        crew_array = []
        try:
            for crew in self.dbINDYCAF.db.volunteers.find({crew_select: True},
                                                          {'_id': 1, gl.DB_FIRST_NAME: 1, gl.DB_LAST_NAME: 1}):
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
                query = {'flight_time': {'$gte': startdate, "$lte": enddate},
                         'airport_code': {'$eq': kwfields["airportcode"]}}
            else:
                query = {'flight_time': {'$gte': startdate, "$lte": enddate}}
        elif "startdate" in kwfields:
            # List all rides after the specified date
            startdate = datetime.strptime(str(kwfields['startdate']), '%Y-%m-%d')
            query = {gl.DB_FLIGHT_TIME: {'$gte': startdate}}
        else:
            # List all flights
            query = {}

        flight_list = []
        try:
            # Get all flights in the date range, maybe all in the future, sorted ascending
            # If there's a failure, Set up error recovery
            # If success, set error message to empty string.
            for flight in self.dbINDYCAF.db.flights.find(query, db_args) \
                    .sort('flight_time', 1):
                if "_id" in flight:
                    id = str(flight["_id"])
                    flight["_id"] = id
                if gl.DB_FLIGHT_TIME in flight:
                    dt = str(flight[gl.DB_FLIGHT_TIME])
                    flight[gl.DB_FLIGHT_TIME] = dt
                flight_list.append(flight)
        except Exception as e:
            print(gl.MSG_GETFLIGHTS_FAILURE, e)
            flight_list = None
            return [flight_list, e]

        return [flight_list, ""]

    # Retrieve flights for a specified day.
    # Convert to JSON
#TODO Maybe delete the following function
    # def bogus_get_flights_for_json(self, *fields, **kwfields):
    #
    #     db_args = {f for f in fields}
    #
    #     if "startdate" in kwfields and 'enddate' in kwfields:
    #         # Find the rides between the two dates
    #
    #         startdate = datetime.strptime(str(kwfields['startdate']), '%Y-%m-%d')
    #
    #         # print(f"enddate: {kwfields['enddate']}")
    #         enddate = datetime.strptime(str(kwfields['enddate']), '%Y-%m-%d')
    #         if "airportcode" in kwfields:
    #             query = {'flight_time': {'$gte': startdate, "$lt": enddate},
    #                      'airport_code': {'$eq': kwfields["airportcode"]}}
    #         else:
    #             query = {'flight_time': {'$gte': startdate, "$lt": enddate}}
    #     elif "startdate" in kwfields:
    #         # List all rides after the specified date
    #         startdate = datetime.strptime(str(kwfields['startdate']), '%Y-%m-%d')
    #         query = {'flight_time': {'$gte': startdate}}
    #     else:
    #         query = {}
    #
    #     try:
    #         flight = self.dbINDYCAF.db.flights.find(query, db_args).sort('flight_time').sort('flight_time', 1)
    #         list_flights = list(flight)
    #         JSONFlights = dumps(list_flights)
    #
    #     except Exception as e:
    #         print('get_flights_for_json: find all failed', e)
    #         JSONFlights = None
    #     # This function return proper JSON. The bson.json import is needed
    #     # to reformat the MongoDB data types
    #     return JSONFlights

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

    def Save_Flight(self, **flightInfo):

        try:
            self.dbINDYCAF.db.flights.insert_one(flightInfo)
            msg = "Flight added to database.\n"
            msg = msg + f"Airport: {flightInfo[gl.DB_AIRPORT_NAME]}\n"
            msg = msg + f"Flight time: {flightInfo[gl.DB_FLIGHT_TIME]}"
            fm = FlaskMail(self.app)
            fm.send_message("Flight Added", "jimolivi@icloud.com", msg)

            return s.database_op_success
        except Exception as e:
            print("Save Flight, insert_one failed: ", e)
            return s.database_op_failure

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
        }, {
            '$lookup': {
                'from': 'volunteers',
                'localField': gl.DB_PILOT,
                'foreignField': '_id',
                'as': gl.DB_PILOT_DETAILS
            }
        }, {
            '$lookup': {
                'from': 'volunteers',
                'localField': gl.DB_CREWCHIEF,
                'foreignField': '_id',
                'as': gl.DB_CREWCHIEF_DETAILS
            }
        }, {
            '$lookup': {
                'from': 'volunteers',
                'localField': gl.DB_CO_PILOT,
                'foreignField': '_id',
                'as': gl.DB_CO_PILOT_DETAILS
            }
        }, {
            '$lookup': {
                'from': 'volunteers',
                'localField': gl.DB_LOAD_MASTER,
                'foreignField': '_id',
                'as': gl.DB_LOAD_MASTER_DETAILS
            }
        }
        ]

        try:
            flights = self.dbINDYCAF.db.flights.aggregate(query)
            for flight in flights:
                return flight
        except Exception as e:
            msg = 'getoneflight: ' + gl.MSG_FIND_OP_FAILED, " " + e
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




