#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Manage Flight Information
#
#   Jim Olivi 2022
#
from datetime import datetime
from globals import globals as gl, NoFlights, signals as s, format_time, scrub_phone
from flask import flash
from bson.json_util import dumps

class Flights:
    def __init__(self, data_base):
        self.db = data_base

# Get all flights.
    def get_flights(self, **kwfields):

        if "startdate" in kwfields:
            start_date = kwfields["startdate"]
            flights = self.db.get_flights(gl.DB_AIRPORT_NAME,
                                          gl.DB_FLIGHT_TIME,
                                          gl.DB_N_NUMBER,
                                          startdate=start_date)
        else:
            flights = self.db.get_flights(gl.DB_AIRPORT_NAME,
                                          gl.DB_FLIGHT_TIME,
                                          gl.DB_N_NUMBER)

        flight_list = []
        if flights is not None and flights[1] == "":
            for flight in flights[0]:
                airplane = self.db.get_one_airplane(flight[gl.DB_N_NUMBER], gl.DB_AIRCRAFT_NAME)
                if airplane is None:
                    flight[gl.DB_AIRCRAFT_NAME] = flight[gl.DB_N_NUMBER] + " " + gl.MSG_AIRPLANE_NOT_ON_DATABASE
                else:
                    if "_id" in airplane:
                        airplane.pop("_id")
                    flight[gl.DB_AIRCRAFT_NAME] = airplane[gl.DB_AIRCRAFT_NAME]

                # str_flight_date = flight[gl.DB_FLIGHT_TIME].strftime("%m/%d/%Y")
                flight[gl.DB_FLIGHT_TIME] = format_time(flight[gl.DB_FLIGHT_TIME])
                flight_list.append(flight)

        return flight_list

# Returns a python dictionary, not JSON-able
    def getfutureflights(self, **req):

        flight_list = self.db.get_flights(gl.DB_AIRPORT_NAME,
                                         gl.DB_AIRPORT_CITY,
                                         gl.DB_AIRPORT_CODE,
                                         gl.DB_FLIGHT_TIME,
                                          gl.DB_NUM_PRIME_SEATS,
                                          gl.DB_NUM_PASS_SEATS,
                                         startdate=req['startdate'])

        # Keep only one per day, do not return other flights.
        # Format the datetime to date only
        if flight_list[0] is None:
            flash(flight_list[1], 'error')
            raise NoFlights

        lastairport = ""
        dayflights = []
        for flight in flight_list[0]:
# TODO See if there are any seats available on this flight

            if lastairport != flight[gl.DB_AIRPORT_CODE]:   # New airport, reset date.
                lastdate = ""    # Initialize date to pick first entry
                lastairport = flight[gl.DB_AIRPORT_CODE]

            date_time = format_time(flight[gl.DB_FLIGHT_TIME])
            date_parts = date_time.split(",")
            flight[gl.DB_FLIGHT_TIME] = date_parts[0]
            date = date_parts[0]

            if lastdate != date:
                lastdate = date
                dayflights.append(flight)

        return dayflights

# Get all flights for one day
    def get_day_flights(self, **req):
        flight_list = self.db.get_flights(gl.DB_N_NUMBER,
                                         gl.DB_AIRPORT_NAME,
                                         gl.DB_AIRPORT_CITY,
                                         gl.DB_AIRPORT_CODE,
                                         gl.DB_FLIGHT_TIME,
                                         gl.DB_FLIGHT_ID,
                                                   startdate=req['startdate'],
                                                   enddate=req['enddate'],
                                                   airportcode=req['airportcode'])


# Get Aircraft Name
        if flight_list[1] != "":
            print(gl.MSG_DATABASE_ERROR)
            print(flight_list[1])
            raise ValueError

        flight_list = flight_list[0]
        for flight in flight_list:
            airplane = self.db.get_one_airplane(flight[gl.DB_N_NUMBER], gl.DB_AIRCRAFT_NAME)
            airplane_name = airplane[gl.DB_AIRCRAFT_NAME]
            # Put the airplane name in the field to be displayed.
            flight[gl.DB_N_NUMBER] = flight[gl.DB_N_NUMBER] + ': ' + airplane_name

        print(flight_list)
        flight_list_json = dumps(flight_list)
        return flight_list_json

# Get one flight by primary key
    def get_one_flight(self, primarykey):

# Might have to format some fields for display
        flight = self.db.get_one_flight(primarykey)
        if flight is None:
            return flight

        flight[gl.DB_FLIGHT_TIME] = str(flight[gl.DB_FLIGHT_TIME])
        if gl.DB_END_FLIGHT_TIME in flight:
            flight[gl.DB_END_FLIGHT_TIME] = flight[gl.DB_END_FLIGHT_TIME]
        else:
            flight[gl.DB_END_FLIGHT_TIME] = ""
        if flight[gl.DB_PILOT] != "Select":
            name = self.db.get_person(flight[gl.DB_PILOT], {gl.DB_FIRST_NAME, gl.DB_LAST_NAME})
            if name is not None:
                flight["pilot_name"] = f"{name[gl.DB_FIRST_NAME]} {name[gl.DB_LAST_NAME]}"
        if flight[gl.DB_CO_PILOT] != "Select":
            name = self.db.get_person(flight[gl.DB_CO_PILOT], {gl.DB_FIRST_NAME, gl.DB_LAST_NAME})
            if name is not None:
                flight["co_pilot_name"] = f"{name[gl.DB_FIRST_NAME]} {name[gl.DB_LAST_NAME]}"
        if flight[gl.DB_CREWCHIEF] != "Select":
            name = self.db.get_person(flight[gl.DB_CREWCHIEF], {gl.DB_FIRST_NAME, gl.DB_LAST_NAME})
            if name is not None:
                flight["crew_chief_name"] = f"{name[gl.DB_FIRST_NAME]} {name[gl.DB_LAST_NAME]}"
        if flight[gl.DB_LOAD_MASTER] != "Select":
            name = self.db.get_person(flight[gl.DB_LOAD_MASTER], {gl.DB_FIRST_NAME, gl.DB_LAST_NAME})
            if name is not None:
                flight["loadmaster_name"] = f"{name[gl.DB_FIRST_NAME]} {name[gl.DB_LAST_NAME]}"
        return flight

    def CreateFlight(self, form, n_number):
        airport_code = form.airport_code.data

        res = self.db.Save_Flight(
            aircraft_n_number=n_number,
            airport_code=airport_code.upper(),
            airport_name=form.airport_name.data,
            prime_price=form.premium_price.data,
            num_prime_seats=form.number_prime_seats.data,
            passenger_price=form.passenger_price.data,
            num_passenger_seats=form.number_pass_seats.data,
            flight_time=form.flight_time.data,
            end_flight_time=form.end_flight_time.data,
            pilot=form.pilots.data,
            co_pilot=form.co_pilots.data,
            crew_chief=form.crew_chiefs.data,
            loadmaster=form.loadmasters.data,
            airport_city=form.airport_city.data
        )
        return res

# Save passenger info for a flight.
    def Passenger(self, passenger_contact_form):

        flight_id = passenger_contact_form.flight_id.data

        flight = self.db.get_one_flight(flight_id, gl.DB_TRANSACTIONS)
        if flight is None:
            flash(f'Filed to read flight record for {flight_id}', 'error')
            return s.database_op_failure

    # Create the new transaction record
        trans_record = {gl.DB_FIRST_NAME: passenger_contact_form.first_name.data,
                        gl.DB_LAST_NAME: passenger_contact_form.last_name.data,
                        gl.DB_ADDRESS: passenger_contact_form.pass_addr.data,
                        gl.DB_CITY: passenger_contact_form.pass_city.data,
                        gl.DB_STATE: passenger_contact_form.state_province.data,
                        gl.DB_POSTAL_CODE: passenger_contact_form.pass_postal.data,
                        gl.DB_EMAIL: passenger_contact_form.pass_email.data,
                        gl.DB_PHONE_NUMBER: scrub_phone(passenger_contact_form.pass_phone.data),
                        gl.DB_FLIGHT_ID: passenger_contact_form.flight_id.data,
                        gl.DB_OK_TO_TEXT: passenger_contact_form.OKtoText.data,
                        gl.DB_TOTAL_PRICE: passenger_contact_form.total_price.data
                        }

        prime_seats = []
        passenger_seats = []
        for passenger in passenger_contact_form.prime_name.raw_data:
            if passenger != '':
                prime_seats.append(passenger)
                flash(f'{passenger}, {gl.MSG_BOOKED}', 'message')

        for passenger in passenger_contact_form.passenger_name.raw_data:
            if passenger != '':
                passenger_seats.append(passenger)
                flash(f'{passenger}, {gl.MSG_BOOKED}', 'message')

        trans_record[gl.DB_PASSENGER_SEATS] = passenger_seats
        trans_record[gl.DB_PRIME_SEATS] = prime_seats
        if gl.DB_TRANSACTIONS not in flight:
            flight[gl.DB_TRANSACTIONS] = []
        flight[gl.DB_TRANSACTIONS].append(trans_record)
        print(flight)
        res = [self.db.update_flight(flight_id, flight)]

        print(res)
        if len(res) == 2:
            # if two elements were returned, an error occurred
            return res[0]

        if res[0] != s.database_op_success:       # If error messages returned
            flash(res[0], 'error')
            return s.database_op_success

