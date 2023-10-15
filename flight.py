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
from aircraft_model import getOneAirplane
from bson.json_util import dumps


# Get one flight by primary key
def get_one_flight(db, primarykey):

# Might have to format some fields for display
    flight = db.get_one_flight(primarykey)
    if flight is None:
        return flight

    flight[gl.DB_FLIGHT_TIME] = flight[gl.DB_FLIGHT_TIME]
    if gl.DB_END_FLIGHT_TIME in flight:
        flight[gl.DB_END_FLIGHT_TIME] = flight[gl.DB_END_FLIGHT_TIME]
    else:
        flight[gl.DB_END_FLIGHT_TIME] = ""
    return flight


def getfutureflights(db, **req):
    flight_list = db.get_flights(gl.DB_AIRPORT_NAME,
                                  gl.DB_AIRPORT_CITY,
                                  gl.DB_AIRPORT_CODE,
                                  gl.DB_FLIGHT_TIME,
                                  gl.DB_SEAT_LIST,
                                    startdate=req['startdate'])

    # Keep only one per day, do not return other flights.
    # Format the datetime to date only
    if flight_list[0] is None:
        flash(flight_list[1], 'error')
        raise NoFlights

    lastAirport = ""
    dayFlights = []
    for flight in flight_list[0]:
        # seats = self.__seatsLeft(flight)

        seats_left = 0
        if gl.DB_SEAT_LIST in flight:
            seats_left = len(flight[gl.DB_SEAT_LIST])

        if seats_left > 0:
            for seat in flight[gl.DB_SEAT_LIST]:
                if seat[gl.DB_TRANSACTION_ID] != "":
                    seats_left = seats_left - 1
        if seats_left > 0:
            if lastAirport != flight[gl.DB_AIRPORT_CODE]:  # New airport, reset date.
                lastDate = ""  # Initialize date to pick first entry
                lastAirport = flight[gl.DB_AIRPORT_CODE]

            date_time = format_time(flight[gl.DB_FLIGHT_TIME])
            date_parts = date_time.split(",")
            flight[gl.DB_FLIGHT_TIME] = date_parts[0]
            date = date_parts[0]

            if lastDate != date:
                lastDate = date
                dayFlights.append(flight)

    return dayFlights

def get_day_flights(db, **req):
    flight_list = db.get_flights(gl.DB_N_NUMBER,
                                      gl.DB_AIRPORT_NAME,
                                      gl.DB_AIRPORT_CITY,
                                      gl.DB_AIRPORT_CODE,
                                      gl.DB_FLIGHT_TIME,
                                      startdate=req['startdate'],
                                      enddate=req['enddate'],
                                      airportcode=req['airportcode'])


    if flight_list[1] != "":
        print(gl.MSG_DATABASE_ERROR)
        print(flight_list[1])
        raise ValueError

    flight_list_json = dumps(flight_list[0])
    return flight_list_json


# Get all flights.
def get_flights(db, **kwfields):

    if "startdate" in kwfields:
        start_date = kwfields["startdate"]
        flights = db.get_flights(gl.DB_AIRPORT_NAME,
                                      gl.DB_FLIGHT_TIME,
                                      gl.DB_N_NUMBER,
                                      startdate=start_date)
        flights = flights[0]
    else:
        flights = db.get_flights(gl.DB_AIRPORT_NAME,
                                      gl.DB_FLIGHT_TIME,
                                      gl.DB_N_NUMBER)

    return flights

class Flight:
    def __init__(self, db, **kwargs):
        self.db = db

        flight_key = None
        if "flight_key" in kwargs:
            flight_key = kwargs[gl.FLIGHT_KEY]

        rider_obj = {
                    gl.DB_NAME: "",
                    gl.DB_ADDRESS: "",
                    gl.DB_CITY: "",
                    gl.DB_STATE: "",
                    gl.DB_POSTAL_CODE: "",
                    gl.DB_BIRTHDATE: "",
            }

        self.flight = {
            gl.DB_AIRPORT_CODE: "",
            gl.DB_AIRPORT_NAME: "",
            gl.DB_AIRPORT_CITY: "",
            gl.DB_N_NUMBER: "",
            gl.DB_FLIGHT_TIME: "",
            gl.DB_END_FLIGHT_TIME: "",
            gl.DB_CREW_LIST: [],
            gl.DB_SEAT_LIST: []
        }

        if flight_key:
            flight = self.db.get_one_flight(flight_key)
            if flight:
    # Scrub the data
                self.flight["_id"] = flight["_id"]
                self.flight[gl.DB_AIRPORT_CODE] = flight[gl.DB_AIRPORT_CODE]
                self.flight[gl.DB_AIRPORT_NAME] = flight[gl.DB_AIRPORT_NAME]
                self.flight[gl.DB_AIRPORT_CITY] = flight[gl.DB_AIRPORT_CITY]
                self.flight[gl.DB_N_NUMBER] = flight[gl.DB_N_NUMBER] if flight[gl.DB_N_NUMBER] is not None else ""

    # Initialize aircraft details
                self.flight[gl.DB_AIRCRAFT_NAME] = ""
                self.flight[gl.DB_AIRCRAFT_TYPE] = ""
                self.flight[gl.DB_AIRCRAFT_IMAGE] = ""

                if gl.DB_AIRCRAFT_DETAILS in flight:
                    if len(flight[gl.DB_AIRCRAFT_DETAILS]) > 0:
                        aircraft_details = flight[gl.DB_AIRCRAFT_DETAILS][0]
                        self.flight[gl.DB_AIRCRAFT_NAME] = aircraft_details[gl.DB_AIRCRAFT_NAME]
                        self.flight[gl.DB_AIRCRAFT_TYPE] = aircraft_details[gl.DB_AIRCRAFT_TYPE]
                        self.flight[gl.DB_AIRCRAFT_IMAGE] = aircraft_details[gl.DB_AIRCRAFT_IMAGE]

                self.flight[gl.DB_FLIGHT_TIME] = flight[gl.DB_FLIGHT_TIME]
                self.flight[gl.DB_END_FLIGHT_TIME] = flight[gl.DB_END_FLIGHT_TIME]
                crew_list = flight[gl.DB_CREW_LIST]
                for crew in crew_list:
                    crew_obj = {
                        gl.DB_COLONEL_NUMBER: crew[gl.DB_COLONEL_NUMBER],
                        gl.DB_FIRST_NAME: crew[gl.DB_FIRST_NAME],
                        gl.DB_LAST_NAME: crew[gl.DB_LAST_NAME],
                        gl.DB_CREW_POSITION: crew[gl.DB_CREW_POSITION]
                    }
                    self.flight[gl.DB_CREW_LIST].append(crew_obj)
                seat_list = flight[gl.DB_SEAT_LIST]
                for seat in seat_list:
                    seat_obj = {
                        gl.DB_SEAT_NAME: seat[gl.DB_SEAT_NAME],
                        gl.DB_SEAT_PRICE: seat[gl.DB_SEAT_PRICE],
                        gl.DB_RIDER_OBJECT: {},
                        gl.DB_TRANSACTION_ID: ""
                    }
                    self.flight[gl.DB_SEAT_LIST].append(seat_obj)


    def create_flight(self, form, colonels, jobs, seat_list, seat_prices, n_number):
        if "Select" in colonels:
            colonels.remove("Select")
        if "" in jobs:
            jobs.remove("")

        crew = list(zip(jobs, colonels))
        crew_list = []
        for job in crew:
            job_dict = {
                gl.DB_CREW_POSITION_NAME : job[0],
                gl.DB_COLONEL_NUMBER: job[1]
            }
            crew_list.append(job_dict)

        seats = list(zip(seat_list, seat_prices))
        seat_list = []
        for seat in seats:
            seat_dict = {
                gl.DB_TRANSACTION_ID: "",
                gl.DB_SEAT_NAME: seat[0],
                gl.DB_SEAT_PRICE: seat[1],
                gl.DB_RIDER: {
                    gl.DB_NAME: "",
                    gl.DB_ADDRESS: "",
                    gl.DB_CITY: "",
                    gl.DB_STATE: "",
                    gl.DB_POSTAL_CODE: "",
                    gl.DB_BIRTHDATE: "",

                }
            }
            seat_list.append(seat_dict)

        self.flight[gl.DB_AIRPORT_CODE] = form.airport_code.data.upper()
        airport = form.airport_name.data
        self.flight[gl.DB_AIRPORT_NAME] = airport
        self.flight[gl.DB_AIRPORT_CITY] = form.airport_city.data
        self.flight[gl.DB_N_NUMBER] = n_number
        self.flight[gl.DB_FLIGHT_TIME] = form.flight_time.data
        self.flight[gl.DB_END_FLIGHT_TIME] = form.end_flight_time.data

        self.flight[gl.DB_CREW_LIST] = crew_list
        self.flight[gl.DB_SEAT_LIST] = seat_list

        self.flight_id = self.db.saveFlight(self.flight)
        return self.flight_id

    def update_flight(self, form, colonels, jobs, seat_list, seat_prices, n_number):
        if "Select" in colonels:
            colonels.remove("Select")
        if "" in jobs:
            jobs.remove("")

        crew = list(zip(jobs, colonels))
        crew_list = []
        for job in crew:
            job_dict = {
                gl.DB_CREW_POSITION_NAME : job[0],
                gl.DB_COLONEL_NUMBER: job[1]
            }
            crew_list.append(job_dict)

        seats = list(zip(seat_list, seat_prices))
        seat_list = []
        for seat in seats:
            seat_dict = {
                gl.DB_TRANSACTION_ID: "",
                gl.DB_SEAT_NAME: seat[0],
                gl.DB_SEAT_PRICE: seat[1],
                gl.DB_RIDER: {
                    gl.DB_NAME: "",
                    gl.DB_ADDRESS: "",
                    gl.DB_CITY: "",
                    gl.DB_STATE: "",
                    gl.DB_POSTAL_CODE: "",
                    gl.DB_BIRTHDATE: "",

                }
            }
            seat_list.append(seat_dict)

        self.flight[gl.DB_AIRPORT_CODE] = form.airport_code.data.upper()
        airport = form.airport_name.data
        self.flight[gl.DB_AIRPORT_NAME] = airport
        self.flight[gl.DB_AIRPORT_CITY] = form.airport_city.data
        self.flight[gl.DB_N_NUMBER] = n_number
        self.flight[gl.DB_FLIGHT_TIME] = form.flight_time.data
        self.flight[gl.DB_END_FLIGHT_TIME] = form.end_flight_time.data

        self.flight[gl.DB_CREW_LIST] = crew_list
        self.flight[gl.DB_SEAT_LIST] = seat_list

        # Scrub the data.
        if gl.DB_AIRCRAFT_NAME in self.flight:
            self.flight.pop(gl.DB_AIRCRAFT_NAME)
        if gl.DB_AIRCRAFT_TYPE in self.flight:
            self.flight.pop(gl.DB_AIRCRAFT_TYPE)
        if gl.DB_AIRCRAFT_IMAGE in self.flight:
            self.flight.pop(gl.DB_AIRCRAFT_IMAGE)

        self.flight_id = self.db.saveFlight(self.flight)
        return self.flight_id


# Save passenger info for a flight.
    def passenger(self, passenger_contact_form):

    # Create the new transaction record
    #     transaction_record = {gl.DB_FIRST_NAME: passenger_contact_form.first_name.data,
    #                     gl.DB_LAST_NAME: passenger_contact_form.last_name.data,
    #                     gl.DB_ADDRESS: passenger_contact_form.pass_addr.data,
    #                     gl.DB_CITY: passenger_contact_form.pass_city.data,
    #                     gl.DB_STATE: passenger_contact_form.state_province.data,
    #                     gl.DB_POSTAL_CODE: passenger_contact_form.pass_postal.data,
    #                     gl.DB_EMAIL: passenger_contact_form.pass_email.data,
    #                     gl.DB_PHONE_NUMBER: scrub_phone(passenger_contact_form.pass_phone.data),
    #                     gl.DB_OK_TO_TEXT: passenger_contact_form.OKtoText.data,
    #                     gl.DB_JOIN_MAILING_LIST: passenger_contact_form.joinMailingList.data,
    #                     gl.DB_CAF_MEMBER: passenger_contact_form.CAFMember.data,
    #                     gl.DB_TOTAL_PRICE: passenger_contact_form.total_price.data
    #                     }

#
# The riders data structure is designed this way in anticipation of various wings
# using this API. The class of seats can be dynamically set up.
#

        i = 0
        seats = []
        seats_sold = 0
        for passenger in passenger_contact_form.passenger_name.raw_data:
            if passenger != '':
                seat = {
                    "seat": "VIP",
                    "name": passenger,
                    # "birthDate": passenger_contact_form.passengerBirthDate.raw_data[i]
                }
                i += 1
                seats.append(seat)
                seats_sold += 1

        seats_dict = self.__seatsLeft(flight)
        if gl.DB_TRANSACTIONS in flight:
            for transaction in flight[gl.DB_TRANSACTIONS]:
                if gl.DB_PRIME in transaction:
                    primeSeatsSold += len(transaction[gl.DB_PRIME_SEATS])
                if gl.DB_VIP in transaction:
                    passengerSeatsSold += len(transaction[gl.DB_VIP])

        if not bool(seats_dict):
            flash(gl.MSG_NO_SEATS_LEFT, 'message')
            return s.failure

        for passenger in passenger_contact_form.prime_name.raw_data:
            if passenger != '':
                flash(f'{passenger}, {gl.MSG_BOOKED}', 'message')
        for passenger in passenger_contact_form.passenger_name.raw_data:
            if passenger != '':
                flash(f'{passenger}, {gl.MSG_BOOKED}', 'message')

        if len(allSeats) > 0:
            transaction_record[gl.DB_SEATS_SOLD] = allSeats

        transaction = {gl.DB_TRANSACTIONS: transaction_record}
        res = self.db.updateFlightArray(flight_id, transaction)

        return res

    def getFlightInfo(self, pass_form):
        # plane = getOneAirplane(self.db, flight[gl.DB_N_NUMBER])
        # if plane is not None:
        # pass_form.prime_seat_price = flight[gl.DB_PRIME_PRICE]
        # pass_form.pass_seat_price = flight[gl.DB_VIP_PRICE]
        # pass_form.flight_id.data = flight_key

        flightTime = str(self.flight[gl.DB_FLIGHT_TIME]).split(" ")
        month = flightTime[0].split("-")[1]
        day = flightTime[0].split("-")[2]
        year = flightTime[0].split("-")[0]
        hour = int(flightTime[1].split(":")[0])
        minute = flightTime[1].split(":")[1]
        hour = hour % 12
        if hour == 0:
            hour = 12
        if hour > 12:
            ampm = "PM"
        else:
            ampm = "AM"
        strFlightTime = f'{month}/{day}/{year} {str(hour)}:{minute}{ampm}'
        pass_form.card_title.label = self.flight[gl.DB_AIRPORT_NAME] + ", " + strFlightTime + " " + self.flight[
            gl.DB_AIRCRAFT_NAME]
        # else:
        #     pass_form.pass_available_seats = 0
        #     pass_form.prime_available_seats = 0
        #     flash(f'{flight[gl.DB_N_NUMBER]}, {gl.MSG_AIRPLANE_NOT_ON_DATABASE}', 'error')
        #     pass_form.card_title.label = gl.MSG_AIRPLANE_NOT_ON_DATABASE

        numPrimeSeats = 0
        numVIPSeats = 0
        primes = ()
        passengers = ()
        if gl.DB_TRANSACTIONS in flight:
            for transaction in flight[gl.DB_TRANSACTIONS]:
                if gl.DB_SEATS_SOLD in transaction:
                    for seat in transaction[gl.DB_SEATS_SOLD]:
                        if seat["seat"] == gl.DB_PRIME:
                            numPrimeSeats += 1
                        elif seat["seat"] == gl.DB_VIP:
                            numVIPSeats += 1

            # Now create the empty seats.
            numPrimeSeats = flight[gl.DB_NUM_PRIME_SEATS] - numPrimeSeats
            for i in range(numPrimeSeats):
                primes = primes + ("",)

            numVIPSeats = flight[gl.DB_NUM_VIP_SEATS] - numVIPSeats
            for i in range(numVIPSeats):
                passengers = passengers + ("",)
        else:
            # No transactions means no seats yet sold.
            for i in range(flight[gl.DB_NUM_PRIME_SEATS]):
                primes = primes + ("",)

            for i in range(flight[gl.DB_NUM_VIP_SEATS]):
                passengers = passengers + ("",)

        return passengers, primes

