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

class Flights:
    def __init__(self, data_base):
        self.db = data_base

# See how many seats are left on a flight.
# Returned is an array: [Prime Seats Sold, Passenger Seats Sold]
    def __seatsLeft(self, flight):
# Must be re-written for new flights structure.
        seats_left = 0

        return seats_left

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
                                          gl.DB_NUM_VIP_SEATS,
                                          gl.DB_TRANSACTIONS,
                                          startdate=req['startdate'])

        # Keep only one per day, do not return other flights.
        # Format the datetime to date only
        if flight_list[0] is None:
            flash(flight_list[1], 'error')
            raise NoFlights

        lastAirport = ""
        dayFlights = []
        for flight in flight_list[0]:
            seats = self.__seatsLeft(flight)
            if bool(seats):
                seats_left = {
                    gl.DB_SEATS_LEFT: seats
                }
                flight.update(seats_left)
                if lastAirport != flight[gl.DB_AIRPORT_CODE]:   # New airport, reset date.
                    lastDate = ""    # Initialize date to pick first entry
                    lastAirport = flight[gl.DB_AIRPORT_CODE]

                date_time = format_time(flight[gl.DB_FLIGHT_TIME])
                date_parts = date_time.split(",")
                flight[gl.DB_FLIGHT_TIME] = date_parts[0]
                date = date_parts[0]

                if lastDate != date:
                    lastDate = date
                    dayFlights.append(flight)

        return dayFlights

# Get all flights for one day
    def get_day_flights(self, **req):
        flight_list = self.db.get_flights(gl.DB_N_NUMBER,
                                          gl.DB_AIRPORT_NAME,
                                          gl.DB_AIRPORT_CITY,
                                          gl.DB_AIRPORT_CODE,
                                          gl.DB_FLIGHT_TIME,
                                          gl.DB_FLIGHT_ID,
                                          gl.DB_NUM_VIP_SEATS,
                                          gl.DB_NUM_PRIME_SEATS,
                                          gl.DB_TRANSACTIONS,
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
            seats = self.__seatsLeft(flight)
            seats_left = {
                gl.DB_SEATS_LEFT: seats
            }
            flight.update(seats_left)

        flight_list_json = dumps(flight_list)
        return flight_list_json

# Get one flight by primary key
    def get_one_flight(self, primarykey):

# Might have to format some fields for display
        flight = self.db.get_one_flight(primarykey)
        if flight is None:
            return flight

        flight[gl.DB_FLIGHT_TIME] = flight[gl.DB_FLIGHT_TIME]
        if gl.DB_END_FLIGHT_TIME in flight:
            flight[gl.DB_END_FLIGHT_TIME] = flight[gl.DB_END_FLIGHT_TIME]
        else:
            flight[gl.DB_END_FLIGHT_TIME] = ""
        return flight

    def create_flight(self, form, crew, crew_positions, seats, seat_prices, n_number):

        crew.remove("Select")
        crew_positions.remove("")
        crew_list = list(zip(crew, crew_positions))

        i = 0
        seat_list = []
        for seat in seats:
            seat_entry = {seat: seat_prices[i], gl.DB_RIDER: None}
            seat_list.append(seat_entry)
            i = i + 1

        new_flight = {
            gl.DB_AIRPORT_CODE: form.airport_code.data.upper(),
            gl.DB_AIRPORT_NAME: form.airport_name.data,
            gl.DB_AIRPORT_CITY: form.airport_city.data,
            gl.DB_N_NUMBER: n_number,
            gl.DB_FLIGHT_TIME: form.flight_time.data,
            gl.DB_END_FLIGHT_TIME: form.end_flight_time.data,
            gl.DB_CREW_LIST: crew_list,
            gl.DB_SEAT_LIST: seat_list
        }
        res = self.db.saveFlight(new_flight)
        return res

# Save passenger info for a flight.
    def passenger(self, passenger_contact_form):

        flight_id = passenger_contact_form.flight_id.data

        flight = self.db.get_one_flight(flight_id)
        if flight is None:
            flash(f'Failed to read flight record for {flight_id}', 'error')
            return s.database_op_failure

    # Create the new transaction record
        transaction_record = {gl.DB_FIRST_NAME: passenger_contact_form.first_name.data,
                        gl.DB_LAST_NAME: passenger_contact_form.last_name.data,
                        gl.DB_ADDRESS: passenger_contact_form.pass_addr.data,
                        gl.DB_CITY: passenger_contact_form.pass_city.data,
                        gl.DB_STATE: passenger_contact_form.state_province.data,
                        gl.DB_POSTAL_CODE: passenger_contact_form.pass_postal.data,
                        gl.DB_EMAIL: passenger_contact_form.pass_email.data,
                        gl.DB_PHONE_NUMBER: scrub_phone(passenger_contact_form.pass_phone.data),
                        gl.DB_OK_TO_TEXT: passenger_contact_form.OKtoText.data,
                        gl.DB_JOIN_MAILING_LIST: passenger_contact_form.joinMailingList.data,
                        gl.DB_CAF_MEMBER: passenger_contact_form.CAFMember.data,
                        gl.DB_TOTAL_PRICE: passenger_contact_form.total_price.data
                        }

        primeSeatsSold = 0
        passengerSeatsSold = 0
        allSeats = []

#
# The riders data structure is designed this way in anticipation of various wings
# using this API. The class of seats can be dynamically set up.
#
        i = 0
        for passenger in passenger_contact_form.prime_name.raw_data:
            if passenger != '':
                seat = {
                    "seat": "Prime",
                    "name": passenger,
                    "birthDate": passenger_contact_form.primeBirthDate.raw_data[i]
                }
                i += 1
                allSeats.append(seat)
                primeSeatsSold += 1

        i = 0
        for passenger in passenger_contact_form.passenger_name.raw_data:
            if passenger != '':
                seat = {
                    "seat": "VIP",
                    "name": passenger,
                    "birthDate": passenger_contact_form.passengerBirthDate.raw_data[i]
                }
                i += 1
                allSeats.append(seat)
                passengerSeatsSold += 1

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

    def getFlightInfo(self, flight, pass_form, flight_key):
        plane = getOneAirplane(self.db, flight[gl.DB_N_NUMBER])
        if plane is not None:
            pass_form.prime_seat_price = flight[gl.DB_PRIME_PRICE]
            pass_form.pass_seat_price = flight[gl.DB_VIP_PRICE]
            pass_form.flight_id.data = flight_key

            flightTime = flight[gl.DB_FLIGHT_TIME].split(" ")
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
            pass_form.card_title.label = flight[gl.DB_AIRPORT_NAME] + ", " + strFlightTime + " " + plane[
                gl.DB_AIRCRAFT_NAME]
        else:
            pass_form.pass_available_seats = 0
            pass_form.prime_available_seats = 0
            flash(f'{flight[gl.DB_N_NUMBER]}, {gl.MSG_AIRPLANE_NOT_ON_DATABASE}', 'error')
            pass_form.card_title.label = gl.MSG_AIRPLANE_NOT_ON_DATABASE

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

