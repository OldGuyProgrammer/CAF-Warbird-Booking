#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Print Fight Report
#
#   Collect flight information from the various databases.
#   Prepare report in .PDF
#   Send .PDF to user computer downloads folder
#
#   Jim Olivi 2023
#
from datetime import datetime
from globals import globals as gl
from bson.objectid import ObjectId

class PrintFlightReport:
    def __init__(self, dataBase, printForm):
        self.db = dataBase
        self.form = printForm

        now = datetime.now()
        self.form .today = now.strftime("%m-%d-%Y")

    def __format_page(self, flight):

        if gl.DB_AIRCRAFT_DETAILS in flight:
            aircraftDetails = flight[gl.DB_AIRCRAFT_DETAILS][0]
            self.form.aircraft = aircraftDetails[gl.DB_AIRCRAFT_NAME]

        self.form.airport = flight[gl.DB_AIRPORT_NAME]
        self.form.flightTime = flight[gl.DB_FLIGHT_TIME]

        self.form.pilotName = gl.MSG_NOT_ASSIGNED
        if gl.DB_PILOT_DETAILS in flight:
            pilot = flight[gl.DB_PILOT_DETAILS]
            if len(pilot) > 0:
                pilot = flight[gl.DB_PILOT_DETAILS][0]
                self.form.pilotName = pilot["_id"] + " " + pilot[gl.DB_FIRST_NAME] + " " + pilot[gl.DB_LAST_NAME]

        self.form.coPilotName = gl.MSG_NOT_ASSIGNED
        if gl.DB_CO_PILOT_DETAILS in flight:
            coPilot = flight[gl.DB_CO_PILOT_DETAILS]
            if len(coPilot) > 0:
                pilot = flight[gl.DB_CO_PILOT_DETAILS][0]
                self.form.coPilotName = coPilot["_id"] + " " + coPilot[gl.DB_FIRST_NAME] + " " + coPilot[gl.DB_LAST_NAME]

        self.form.crewChiefName = gl.MSG_NOT_ASSIGNED
        if gl.DB_CREWCHIEF_DETAILS in flight:
            crewChief = flight[gl.DB_CREWCHIEF_DETAILS]
            if len(crewChief) > 0:
                crewChief = flight[gl.DB_CREWCHIEF_DETAILS][0]
                self.form.crewChiefName = crewChief["_id"] + " " + crewChief[gl.DB_FIRST_NAME] + " " + crewChief[gl.DB_LAST_NAME]

        self.form.loadMasterName = gl.MSG_NOT_ASSIGNED
        if gl.DB_LOAD_MASTER_DETAILS in flight:
            loadMaster = flight[gl.DB_LOAD_MASTER_DETAILS]
            if len(loadMaster) > 0:
                loadMaster = flight[gl.DB_LOAD_MASTER_DETAILS][0]
                self.form.loadMasterName = loadMaster["_id"] + " " + loadMaster[gl.DB_FIRST_NAME] + " " + loadMaster[gl.DB_LAST_NAME]

        if gl.DB_TRANSACTIONS in flight:
            for transaction in flight[gl.DB_TRANSACTIONS]:
                self.form.purchaser = f"{transaction[gl.DB_FIRST_NAME]} " \
                       f"{transaction[gl.DB_LAST_NAME]}"
                if transaction[gl.DB_PHONE_NUMBER] != "":
                    self.form.phoneNumber = transaction[gl.DB_PHONE_NUMBER]
                    if transaction[gl.DB_OK_TO_TEXT]:
                        self.form.okToText = "OK"
                    else:
                        self.form.okToText = " Not OK"
                # if transaction[gl.DB_EMAIL] != "":
                #     line += f", {transaction[gl.DB_EMAIL]}"
                self.primes = []
                if gl.DB_PRIME_SEATS in transaction:
                    for prime in transaction[gl.DB_PRIME_SEATS]:
                        self.primes.append(prime)
                self.passengers =[]
                if gl.DB_PASSENGER_SEATS in transaction:
                    for passenger in transaction[gl.DB_PASSENGER_SEATS]:
                        self.passengers.append(passenger)
        else:
            print(gl.MSG_NO_FLIGHTS)
            # self.pdf.write_line(gl.MSG_NO_FLIGHTS)
        return


    def get_flights(self, flight_ids):
        flight_array = flight_ids.split(",")

        flights = []
        for flight_id in flight_array:
            # msg = gl.MSG_FLIGHT_REPORT_REQUESTED + ": " + flight_id
            # print(msg)

            flight = self.db.get_one_flight(flight_id)
            if flight is not None:
# Scrub the flight record
                flight["_id"] = str(flight["_id"])
                flight[gl.DB_FLIGHT_TIME] = str(flight[gl.DB_FLIGHT_TIME])
                if gl.DB_END_FLIGHT_TIME in flight:
                    flight[gl.DB_END_FLIGHT_TIME] = str(flight[gl.DB_END_FLIGHT_TIME])
                if gl.DB_PILOT_DETAILS in flight:
                    if len(flight[gl.DB_PILOT_DETAILS]) == 0:
                        flight.pop(gl.DB_PILOT_DETAILS)
                if gl.DB_CO_PILOT_DETAILS in flight:
                    if len(flight[gl.DB_CO_PILOT_DETAILS]) == 0:
                        flight.pop(gl.DB_CO_PILOT_DETAILS)
                if gl.DB_CREWCHIEF_DETAILS in flight:
                    if len(flight[gl.DB_CREWCHIEF_DETAILS]) == 0:
                        flight.pop(gl.DB_CREWCHIEF_DETAILS)
                if gl.DB_LOAD_MASTER_DETAILS in flight:
                    if len(flight[gl.DB_LOAD_MASTER_DETAILS]) == 0:
                        flight.pop(gl.DB_LOAD_MASTER_DETAILS)
                if gl.DB_AIRCRAFT_DETAILS in flight:
                    if len(flight[gl.DB_AIRCRAFT_DETAILS]) == 0:
                        flight.pop(gl.DB_AIRCRAFT_DETAILS)

                flights.append(flight)
                # self.__format_page(flights)

        return flights


