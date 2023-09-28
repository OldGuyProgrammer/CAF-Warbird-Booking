#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         constants
#
#   Jim Olivi 2002
#

from flask import flash
from enum import Enum
import json
import os

# Database variable names
class globals:
    # Use USERID as the label for the key field.
    # Map it to the required Key id for the database chosen. The database module will do the mapping.
    # For MongoDB, each record must have a key called "_id".
    # For MongoDB, if the _id is not specified, MongoDB will create a random one.

    DB_ACTIVE = 'active'
    DB_ADDRESS = 'address'
    DB_AIRCRAFT_DETAILS = "aircraftDetails"
    DB_AIRPORT_CODE = "airport_code"
    DB_AIRPORT_NAME = "airport_name"
    DB_AIRPORT_CITY = 'airport_city'
    DB_AIRCRAFT_NAME = "aircraft_name"
    DB_AIRCRAFT_IMAGE = 'aircraft_image_file_name'
    DB_AIRCRAFT_OPERATIONAL = "operational"
    DB_AIRCRAFT_TYPE = "aircraft_type"
    DB_AUTHENTICATED = 'authenticated'
    DB_CAF_MEMBER = "CAFMember"
    DB_CREW_LIST = "crew_list"
    DB_CITY = "city"
    DB_CREW = "crew"
    DB_CREW_POSITIONS = "crew_positions"
    DB_CREW_POSITION = "crew_position"
    DB_COLONEL_NUMBER = "colonel_number"
    DB_MM_DD_YYYY = "%m-%d-%Y"
    DB_EMAIL = 'email_address'
    DB_END_FLIGHT_TIME = "end_flight_time"
    DB_FIRST_NAME = 'first_name'
    DB_FLIGHT_ID = 'flight_id'  # Maps Fight ID to MongoDB _id
    DB_FLIGHT_TIME = "flight_time"
    DB_JOIN_MAILING_LIST = "mailing_list"
    DB_LAST_NAME = 'last_name'
    DB_MANIFEST = 'manifest'
    DB_N_NUMBER = "aircraft_n_number"
    DB_NEW_PASSWORD = 'new_password'
    DB_NUM_ENGINES = 'number_engines'
    DB_NUM_PRIME_SEATS = 'num_prime_seats'
    DB_NUM_VIP_SEATS = 'num_VIP_seats'
    DB_PHONE_NUMBER = 'pass_phone'
    DB_OK_TO_TEXT = 'ok_to_text'
    DB_PASSWORD = 'password'
    DB_PASS_NAME = 'passenger_name'
    DB_PASSENGERS = 'passengers'
    DB_PRIME = "Prime"
    DB_PASSENGER_ID = "passenger_id"         # Maps passenger ID to MongoDB _id
    DB_PRIME_PASS_NAME = 'prime_pass_name'
    DB_PRIME_PRICE = "prime_price"
    DB_RIDER = "Rider"
    DB_SEAT_LIST = "seat_list"
    DB_TRANSACTIONS = 'transactions'
    DB_POSTAL_CODE = "postalCode"
    DB_RECORD_KEY = "record_id"
    DB_STATE = "state"
    DB_VOLUNTEER_ON_FILE = "volunteer_on_file"

# Screen Prompts
    PR_ADDRESS = 'Address'
    PR_ADD_A_FLIGHT = 'Add/Update This Flight'
    PR_ADD_AIRCRAFT = 'Add Aircraft'
    PR_ADMIN = "Admin"
    PR_AIRCRAFT_N_NUMBER = 'N Number'
    PR_AIRCRAFT_NAME = 'Aircraft Name'
    PR_AIRCRAFT_TYPE = 'Aircraft Type'
    PR_AIRCRAFT_OPERATIONAL = "Operational"
    PR_AIRCRAFT_PHOTO = 'Choose a photo of your aircraft (PNG, JPG, JPEG)'
    PR_AIRPORT_NAME = 'Airport Name'
    PR_AIRPORT_CITY = 'Airport City'
    PR_BIRTH_DAY = "Birthday"
    PR_CAF_MEMBER = "CAF Member"
    PR_CREW_ADD_BUTTON = "Add Crew"
    PR_CREW_POSITION = "Crew Position"
    PR_CITY = 'City'
    PR_COLONEL_NUMBER = "Col #"
    # PR_CREWCHIEF = "Crew Chief"
    PR_END_FLIGHT_TIME = 'Ending Flight Time: '
    PR_FIRST_NAME = 'First Name'
    PR_FLIGHT_TIME = 'Starting Flight Time: '
    PR_IATA_CODE = 'IATA'
    PR_JOIN_MAILING_LIST = "Join the mailing list."
    PR_LAST_NAME = 'Last Name'
    # PR_LOADMASTER = "Load Master"
    PR_EMAIL = 'Email Address'
    PR_HOLD_HARMLESS = "Sign Form"
    PR_NEW_PASSWORD = "New Password"
    PR_NUM_ENGINES = 'Number of Engines'
    PR_NUMBER_SEATS = 'Number: '
    PR_OK_TEXT = 'OK To Text'
    PR_PHONE = 'Mobile Phone'
    # PR_PILOT = "Pilot"
    PR_POSTAL = 'Zip/Postal'
    PR_PASS_NAME = 'Enter Passenger Name'
    PR_PASSWORD = "Password"
    PR_PRICE = 'Price: '
    PR_PAY_FOR_FLIGHT = 'Pay For Flight'
    PR_PRINT_MANIFEST = "Print Manifest"

# Screen and Report Labels
    LBL_AIRCRAFT = "Aircraft"
    LBL_AIRPORT = "Airport"
    LBL_TOTAL = "Total"
    LBL_NEW_PASSWORD = 'New Password'
    LBL_PASSWORD = 'New Password'

# Manifest Labels
    MN_AIRCRAFT_TYPE = 'AIRCRAFT TYPE'
    MN_ARRIVAL = 'ARRIVAL'
    MN_CHOOSE_AIRPORT = 'Choose Airport'
    MN_CREW_CHIEF_NAME = "ENG_NAME"
    MN_CREW_CHIEF_ID = "crew_chief_id"
    MN_DEPARTURE_POINT = 'DEPARTURE POINT'
    MN_FLT_ENGINEER = 'FLIGHT ENGINEER'
    MN_LOAD_MASTER_NAME = "Load_Master"
    MN_LOAD_MASTER_ID = "load_master_id"
    MN_PIC = 'PIC_NAME'
    MN_PIC_ID = "PilotID"
    MN_SELECT_A_FLIGHT = 'Select a Flight'
    MN_SIC = 'SIC'
    MN_SIC_ID = 'co_pilot_id'

# Mail Merge Labels
# This set defines the Google Mail Merge fields based on the CAF Manifest from CAFR 60-1
# There are eleven rows for crew and passenger signatures
    MM_AIRCRAFT_TYPE = "AIR_TYPE"
    MM_ARRIVAL = "ARR"
    MM_DEPART = "DEPART"
    MM_ENG = "ENG"
    MM_PIC = "PIC"
    MM_SIC = "SIC"
    MM_LOAD_MASTER = "LM"
    MM_PRIME = "Prime"

#Messages
    MSG_GET_IATA_FAILED = "Get Airport Code variables failed:"
    MSG_AIRPORT_API_KEY_PROBLEM = "Airport service API Key problem."
    MSG_AIRPLANE_ADDED = 'Airplane Added.'
    MSG_AIRPLANE_ON_FILE = 'Airplane N-number found on file.'
    MSG_AIRPLANE_PHOTO_EXISTS = 'The airplane photo is already on file.'
    MSG_AIRPLANE_UNABLE_TO_SAVE = 'Unable to save airplane photo.'
    MSG_AIRPLANE_NOT_ON_DATABASE = 'not found on database.'
    MSG_ADD_NEW_FAILED = "Add New Volunteer Failed: "
    MSG_BOOKED = 'booked on flight'
    MSG_COMPLETE_ADDRESS = "Complete Address"
    MSG_DATABASE_ERROR = "Database error. Processing stopped. See messages..."
    MSG_DATE_ENTERED = " Date entered: "
    MSG_DATE_ERROR = "Date format should be mm/dd/yyyy, ie: 3/16/1954"
    MSG_ENTER_ADDRESS = "Enter Address"
    MSG_ENTER_POSTAL_CODE = "Enter Postal Code"
    MSG_FLIGHT_REPORT_REQUESTED = "Flight report requested for"
    MSG_FLIGHT_ID_REQUIRED = "Flight ID required."
    MSG_GET_TRANSACTION_FAILED = "Get transaction failed: "
    MSG_LOGIN_FAILED = "Login Failed, Contact system administrator."
    MSG_CONTACT_ADMIN = "If problem persists, contact administrator"
    MSG_NO_FLIGHTS = "There are no flights with available seats in the dates requested"
    MSG_GETFLIGHTS_FAILURE = 'GetFlights: find() failed'
    MSG_GOOGLE_MAIL_MERGE_FAILURE = "Google Mail Merge Failure"
    MSG_ENTER_NAME = 'Please enter your name'
    MSG_FLIGHT_ID_REQ = "Flight ID is required"
    MSG_CONTACT = 'Needed to contact you.'
    MSG_NEW_PASSWORD_SAME_AS_OLD = "Password change must be a different password"
    MSG_NO_PASSENGER_SEATS = "No passenger seats available."
    MSG_NO_PRIME_SEATS = "No prime seats available."
    MSG_NOT_ASSIGNED = "Position not assigned."
    MSG_RESERVATION_MISSING = "Reservation information missing."
    MSG_PASSWORD_CHANGE_SUCCESS = "Your password was changed."
    MSG_UPDATE_FLIGHT_FAILED = "Update Flight Failed: "
    MSG_UPDATE_VOL_FAILED = "Update Volunteer Failed: "
    MSG_SAVE_PASSENGERS_FAILED = "Save passenger failed: "
    MSG_SAVE_TRANSACTION_FAILED = "Save transaction failed: "
    MSG_START_DATE = "Start date: "
    MSG_FIND_OP_FAILED = 'find op failed'
    MSG_N_NUMBER = 'Aircraft N Numbers: capital letters and numbers only'
    MSG_MESSAGE_SENT = "Message Sent"
    MSG_FLIGHT_NOT_FOUND = "Flight not on database."
    MSG_TWO_DATES_REQUIRED = "Date range required to retrieve flights by date."
    MSG_VOLUNTEER_NOT_FOUND = "Volunteer not found."

#URL parameters
    URL_DATE = "date"

# Enumerated signals to send and receive messages between modules.
class signals(Enum):
    success = 1
    failure = 2
    volunteer_on_file = 3
    volunteer_not_on_file = 4
    password_not_matched = 5
    database_op_success = 6
    database_op_failure = 7
    duplicate_volunteer_id = 8
    duplicate_aircraft_id = 9
    no_flights = 10
    userid_required = 11


class NoFlights(Exception):
    def __init__(self, message=globals.MSG_NO_FLIGHTS):
        self.message = message
        super().__init__(self.message)


def DisplayFlask(form):
    for fieldName, errorMsg in form.errors.items():
        for msg in errorMsg:
            display_msg = f'{fieldName}: {msg}'
            flash(display_msg, "error")
            print(display_msg)

def format_time(date_time):
    dt_parts = date_time.split(" ")
    date = dt_parts[0]
    time = dt_parts[1]
    date_parts = date.split("-")
    year = date_parts[0]
    month = date_parts[1]
    day = date_parts[2]
    time_parts = time.split(":")
    hour = time_parts[0]
    minute = time_parts[1]
    if int(hour) < 12:
        ampm = "AM"
    else:
        hour = int(hour) % 12
        ampm = "PM"
    formatted_dt = f"{month}/{day}/{year}, {hour}:{minute} {ampm}"
    return formatted_dt

def scrub_phone(phone) :
    scrubbed_phone = ''
    for i in phone:
        if i in '0123456789':
            scrubbed_phone += i

    return scrubbed_phone
class StateList:

    def __init__(self, app):
    # Load the state table
        try:
            path = app.root_path
            fullpath = path + '/static/resources/statecode.json'
            with open(fullpath, 'r') as state_file:
                states_and_provinces = json.load(state_file)
        except FileNotFoundError as e:
            print("Unable to open state code file.")
            print(e)
        else:
            state_list = {" ": " "}
            for state in states_and_provinces[0]["states"]:
                state_list[state["name"]] = state["abbreviation"]
            for province in states_and_provinces[1][0]["states"]:
                state_list[province["name"]] = province["abbreviation"]

            self.sorted_states = {}
            for state in sorted(state_list):
                self.sorted_states[state] = state_list[state]

    def getstatelist(self):
        states = self.sorted_states
        states_array = [(v, k) for k, v in states.items()]
        return states_array

