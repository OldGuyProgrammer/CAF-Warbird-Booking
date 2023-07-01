#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Main module
#
#   Jim Olivi 2022
#

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import os
import configparser
from datetime import date, datetime, timedelta
import json
import asyncio
from flask_bootstrap import Bootstrap

from forms import LoginForm, AddVolunteer, CreateFlightForm, PassengerContact, AddAircraft, Manifest, FindMyRide, Home, FlightReport
from database import DatabaseManager
from print_flight_report import PrintFlightReport
from manifest import Manifests
from flights import Flights
from security import Security
from globals import signals as s, globals as gl, NoFlights, DisplayFlask, StateList, scrub_phone
from airports import airports
from volunteer import Volunteer, getLists
from customer_manager import Customer
from aircraft_model import getAirPlanes
# from square import SquareServices as Square

print("Indiana Commemorative Air Force")
print("Warbirds Rides Booking System started.")

print(f"main module name: {__name__}")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['REMEMBER_COOKIE_DURATION'] = os.getenv('COOKIE_DURATION')
Bootstrap(app)

db = DatabaseManager(app)
# Un-comment the following to initialize a new Volunteer database
# initial_vol = {
#     gl.DB_RECORD_KEY: "11111",
#     gl.DB_PASSWORD: "password",
#     gl.DB_FIRST_NAME: "",
#     gl.DB_LAST_NAME: "",
#     gl.DB_ADMIN: False,
#     gl.DB_PILOT: False,
#     gl.DB_CREWCHIEF: False,
#     gl.DB_LOAD_MASTER: False
# }
# vol = Volunteer(db, "11111")
# vol.update_volunteer(app, initial_vol)
###############################################

# I looked at MongoEngine (Flask) and decided to stay with pymongo
# pymongo exposes more of the MongoDB features.

# Set up the Flask Login Manager to authenticate users.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

config = configparser.ConfigParser()

@login_manager.user_loader
def load_user(user_id):
    vol_obj = Volunteer(db, user_id)
    return vol_obj


@app.route("/")
def home():
    # See if there is a session for this user.
    # Retrieve the user id
    # get volunteer info from the database
    home = Home()
    sec = Security(app)
    user_id = sec.get_user_id
    vol = Volunteer(db, user_id)
    home.is_authenticated = vol.is_authenticated
    home.FirstName = vol.firstname
    home.LastName = vol.lastname
    return render_template('index.html', form=home), 200


# Login the volunteer. The UserId should be a colonel number
# TODO find a way to retrieve Colonel numbers from HQ

@app.route("/login", methods=['POST', 'GET'])
def login():
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        vol = Volunteer(db, login_form.userid.data)

        if vol is None:
            flash(g.MSG_LOGIN_FAILED, "error")
            flash(gl.MSG_CONTACT_ADMIN, "error")
            return redirect(url_for('login'))

        res = vol.login_volunteer(login_form, app)
        if res == s.success:
            login_user(vol)
            next_url = login_form.next_url.data
            if next_url != "":
                return redirect(next_url)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

    # Display the login form
    next_url = request.args.get('next')

    if next_url is not None:
        login_form.next_url.data = next_url
    return render_template('login.html', form=login_form), 200


@app.route("/signout", methods=['GET'])
def sign_out():
    sec = Security(app)
    user_id = sec.get_user_id
    db.update_volunteer(user_id, {gl.DB_AUTHENTICATED:  False})
    logout_user()
    return redirect(url_for('home'))


# Add a volunteer (CAF Member) to the database.
# Also used to change password.
@app.route("/addvolunteer", methods=['POST', 'GET'])
@login_required
def add_volunteer():

    add_volunteer_form = AddVolunteer(request.form)
    if request.method == "POST" and add_volunteer_form.validate():

        vol = Volunteer(db, add_volunteer_form.record_id.data)
        new_volunteer = {
            gl.DB_RECORD_KEY: add_volunteer_form.record_id.data,
            gl.DB_FIRST_NAME: add_volunteer_form.FirstName.data,
            gl.DB_LAST_NAME: add_volunteer_form.LastName.data,
            gl.DB_ADMIN: add_volunteer_form.admin.data,
            gl.DB_PILOT: add_volunteer_form.pilot.data,
            gl.DB_CREWCHIEF: add_volunteer_form.crew_chief.data,
            gl.DB_LOAD_MASTER : add_volunteer_form.loadmaster.data,
            gl.DB_PASSWORD: add_volunteer_form.password.data,
            # gl.DB_NEW_PASSWORD: add_volunteer_form.new_password.data
        }
        res = vol.update_volunteer(app, new_volunteer)

        if res == s.duplicate_volunteer_id:
            flash(f"{request.form['first_name']}, {request.form['last_name']}", "error")
            return redirect(url_for('addvolunteer'))
        else:
           return redirect(url_for('add_volunteer'))
    else:
        DisplayFlask(add_volunteer_form)

    return render_template('addvolunteer.html', form=add_volunteer_form), 200


# Get all flights for the requested airport
@app.route("/getairport/<airportCode>", methods=['GET'])
def getairport(airportCode):
    return airports.get_airport_info(airportCode), 201


# Add an aircraft to the database.
@app.route("/addaircraft", methods=['POST', 'GET'])
@login_required
def add_aircraft():

    add_aircraft_form = AddAircraft(request.form)
    if request.method == "POST" and add_aircraft_form.validate():
        am = ap(db)
        airplane_data = add_aircraft_form.data
        file = request.files[gl.DB_AIRCRAFT_IMAGE]
        if file.filename != "":
            filename = secure_filename(file.filename)
            fullpath = app.root_path + "/static/images/" + filename
            try:
                file.save(fullpath)
                file.close()
            except FileExistsError:
                flash(gl.MSG_AIRPLANE_PHOTO_EXISTS, "message")
                flash(f"{airplane_data[gl.DB_AIRCRAFT_NAME]} {add_aircraft_form.aircraft_n_number.data}.", 'message')
            except FileNotFoundError as err:
                flash(gl.MSG_AIRPLANE_UNABLE_TO_SAVE, 'error')
                flash(err, 'error')
                return render_template('seriouserror.html'), 500
            except Exception as err:
                print(err)
                flash(gl.MSG_AIRPLANE_UNABLE_TO_SAVE, 'error')
                flash(err, 'error')
                return render_template('seriouserror.html'), 500

        if 'csrf_token' in airplane_data:
            airplane_data.pop('csrf_token')
        if 'add_aircraft' in airplane_data:
            airplane_data.pop('add_aircraft')

        airplane_data[gl.DB_AIRCRAFT_IMAGE] = filename
        res = am.AddAircraft(airplane_data)
        if res == s.database_op_success:
            flash(gl.MSG_AIRPLANE_ADDED, "message")
            flash(f"{airplane_data[gl.DB_AIRCRAFT_NAME]} {add_aircraft_form.aircraft_n_number.data} added.", 'message')
        elif res == s.duplicate_aircraft_id:
            flash(gl.MSG_AIRPLANE_ON_FILE, "error")
            flash(f"{airplane_data[gl.DB_AIRCRAFT_NAME]} {add_aircraft_form.aircraft_n_number.data} Not Added", 'error')

        return redirect(url_for('add_aircraft', method="GET"))
    else:
        DisplayFlask(add_aircraft_form)

    return render_template('addaircraft.html', form=add_aircraft_form), 200

# Get one volunteer record
@app.route("/getvolunteer", methods=["GET"])
@login_required
def getvolunteer():
    user_id = request.args.get(gl.DB_RECORD_KEY, None)
    vol = Volunteer(db, user_id)
    vol_data = vol.person_data
    scrubbed_vol = {
        gl.DB_RECORD_KEY: vol_data[gl.DB_RECORD_KEY],
        gl.DB_FIRST_NAME: vol_data[gl.DB_FIRST_NAME],
        gl.DB_LAST_NAME: vol_data[gl.DB_LAST_NAME],
        gl.DB_ADMIN: vol_data[gl.DB_ADMIN],
        gl.DB_PILOT: vol_data[gl.DB_PILOT],
        gl.DB_CREWCHIEF: vol_data[gl.DB_CREWCHIEF],
        gl.DB_LOAD_MASTER: vol_data[gl.DB_LOAD_MASTER]
    }
    return scrubbed_vol

# Create a new flight at an airport/airshow
@app.route("/createflight", methods=['POST', 'GET'])
@login_required
def createflight():

    fl = Flights(db)
    cff = CreateFlightForm(request.form)
    if request.method == "POST" and cff.validate():
        airport_code = cff.airport_code.data
        n_number = request.form.get("aircraft_name")
        flight_time = cff.flight_time.data
        if fl.CreateFlight(cff, n_number):
            flash("Flight Added.", 'message')
            flash(f'{airport_code}, {n_number}, {flight_time}', 'message')

        return redirect(url_for('createflight', method="GET"))
    elif request.method == "GET":
        DisplayFlask(cff)

        lists = asyncio.run(getLists(db))
        airplanes = asyncio.run(getAirPlanes(db))

        pilot_list = lists[0].copy()
        lists.insert(0, pilot_list)
        args = request.args.to_dict()  # Get the params
        if "flightkey" in args:
            flight = fl.get_one_flight(args['flightkey'])
            cff.airport_code.data = flight[gl.DB_AIRPORT_CODE]
            cff.airport_name.data = flight[gl.DB_AIRPORT_NAME]
            cff.airport_city.data = flight[gl.DB_AIRPORT_CITY]
            # Date time will format correctly if its in datetime format
            cff.flight_time.data = flight[gl.DB_FLIGHT_TIME]
            cff.end_flight_time.data = flight[gl.DB_END_FLIGHT_TIME]
            cff.premium_price.data = flight[gl.DB_PRIME_PRICE]
            cff.passenger_price.data = flight[gl.DB_PASSENGER_PRICE]
            cff.number_prime_seats.data = flight[gl.DB_NUM_PRIME_SEATS]
            cff.number_pass_seats.data = flight[gl.DB_NUM_PASS_SEATS]
            if "pilot" in flight:
                cff.pilots.default = flight['pilot']
            else:
                lists[0].insert(0, ("Select", "Select"))
            if "co_pilot_name" in flight:
                cff.co_pilots.default = flight['co_pilot_name']
            else:
                lists[1].insert(0, ("Select", "Select"))
            if "crew_chief_name" in flight:
                cff.crew_chiefs.default = flight['crew_chief_name']
            else:
                lists[2].insert(0, ("Select", "Select"))
            if "loadmaster_name" in flight:
                cff.loadmasters.default = flight['loadmaster_name']
            else:
                lists[3].insert(0, ("Select", "Select"))

        else:
            lists[0].insert(0, ("Select", "Select"))
            lists[1].insert(0, ("Select", "Select"))
            lists[2].insert(0, ("Select", "Select"))
            lists[3].insert(0, ("Select", "Select"))
            airplanes.insert(0, ("Select", "Select"))

        cff.pilots.choices = lists[0]
        cff.co_pilots.choices = lists[1]
        cff.crew_chiefs.choices = lists[2]
        cff.loadmasters.choices = lists[3]

        cff.process()
    else:
        DisplayFlask(cff)

    return render_template('createflight.html', form=cff, airplanes=airplanes), 201

# Show all flights for selection to edit
@app.route("/selectflight", methods=["GET"])
@login_required
def select_flight():

    fl = Flights(db)
    flight_list = fl.get_flights()
    if flight_list is None:
        flash(gl.MSG_NO_FLIGHTS, 'message')
        flight_list = {}

    return render_template("selectflight.html", flights=flight_list), 201


# Print the Flight Report
@app.route("/printFlightReport", methods=["GET"])
# @login_required
def print_flight_report():
    frf = FlightReport()
    fr = PrintFlightReport(db, frf)

    flight_ids = request.args.get("flightid", None)
    if flight_ids is not None:
        flights = fr.get_flights(flight_ids)
    else:
        print(gl.MSG_FLIGHT_ID_REQUIRED)
        flash(gl.MSG_FLIGHT_ID_REQUIRED)

    return render_template("flightreport.html", flights=flights), 201

# Print the manifest
@app.route("/printManifest", methods=["GET"])
@login_required
def printManifest():

    flight_id = request.args.get(gl.DB_FLIGHT_ID, None)
    if flight_id is not None:
        man = Manifests(db)
        return_from_manifest = man.get_manifest(flight_id)
# The .pdf of the manifest is returned as a binary blob.
        if return_from_manifest[0] == s.failure:
            print(return_from_manifest[1])
            msg = {
                "error": gl.MSG_GOOGLE_MAIL_MERGE_FAILURE,
                "msg": "Internal Google Mail Merge Failure"
            }
            return msg, 500

        return return_from_manifest[1], 201

    else:
        DisplayFlask(gl.MSG_FLIGHT_ID_REQ)
        return gl.MSG_FLIGHT_ID_REQ

# ----------------------------------------------------------------
# Create flight manifest
#
# Read the flight record. Parse out all flight information.
# Format it for the Google Mail merge

@app.route("/manifest", methods=['GET'])
# @login_required
def manifest():

    flight_id = request.args.get(gl.DB_FLIGHT_ID, None)

    if flight_id is not None:
        man = Manifests(db)
        manifest_data = man.get_manifest_info(flight_id)
        crew = manifest_data[0]
        passenger_list = manifest_data[1]
        header = manifest_data[2]

        manifest_scratch = {
            gl.DB_MANIFEST: {
                gl.DB_AIRPORT_CODE: header[gl.DB_AIRPORT_CODE],
                gl.DB_AIRCRAFT_TYPE: header[gl.DB_AIRCRAFT_TYPE],
                gl.DB_N_NUMBER: header[gl.DB_N_NUMBER],
                gl.DB_CREW: {
                    gl.DB_PILOT: crew[gl.MN_PIC],
                    gl.DB_CO_PILOT: crew[gl.MN_SIC],
                    gl.DB_CREWCHIEF: crew[gl.MN_CREW_CHIEF_NAME],
                    gl.DB_LOAD_MASTER: crew[gl.MN_LOAD_MASTER_NAME]},
                gl.DB_PASSENGERS: {
                    gl.DB_PASSENGERS: passenger_list
                }
            }
        }

        return json.dumps(manifest_scratch), 201

    manifest_form = Manifest()
    fl = Flights(db)
    flights = fl.getfutureflights(startdate=date.today())

    air_ports = [('Select','Select')]
    for flight in flights:
        value = f'{flight[gl.DB_AIRPORT_CODE]}-{flight[gl.DB_FLIGHT_TIME]}'
        label = f'{flight[gl.DB_AIRPORT_NAME]} {flight[gl.DB_FLIGHT_TIME]}'
        selection = (value, label)
        air_ports.append(selection)

    manifest_form.airport_codes.choices = air_ports

    return render_template('manifest.html', form=manifest_form), 200

# ----------------------------------------------------------------
# Call Credit Card Processor
#
# This display specific credit card processor API page.
# The code can be swapped out for any card processor needed.

@app.route('/creditcard')
def creditcard():
    sq = Square()
    sq.get_token()
    return render_template('creditcard.html')


@app.route('/payment', methods=["POST"])
def payment():
    print("Enter Payment Routine")
    req_JSON = request.get_json()
    print(req_JSON)
    return "<h1>Payment Stuff Received</h1>"

# ----------------------------------------------------------------

# Ride With Us section
@app.route("/ridewithus", methods=['GET'])
def ridewithus():
    fl = Flights(db)
    try:
        day_flights = fl.getfutureflights(startdate=date.today())
    except NoFlights:
        flash(gl.MSG_NO_FLIGHTS, 'message')
        # day_flights = s.no_flights
        return render_template('seriouserror.html'), 406

    return render_template('ridewithus.html', flights=day_flights), 200


@app.route("/passengercontact", methods=['GET', 'POST'])
def passenger_contact():

    fl = Flights(db)
    pass_form = PassengerContact()

    if request.method == 'POST':
        res = fl.passenger(pass_form)
        if res == s.database_op_success:
            return redirect(url_for('ridewithus'))
        else:
            return render_template('seriouserror.html'), 500
        # else:
        #     for error in pass_form.errors:
        #         flash(f'Field: {error}: {pass_form.errors[error]}', 'error')
        #
        #     pass_form.pass_available_seats = 0
        #     pass_form.prime_available_seats = 0
        #     return render_template('passengercontact.html', form=pass_form), 201

    elif request.method == "GET":
        flight_key = request.args.get('flightkey', None)
        if flight_key is None:
            flash(gl.MSG_FLIGHT_ID_REQ, 'error')
            return render_template('seriouserror.html'), 406

# TODO Find My Flight can no longer get the transaction separately
        sl = StateList(app)
        pass_form.state_province.choices = sl.getstatelist()
        flight = fl.get_one_flight(flight_key)
        if flight is None:
            flash(gl.MSG_FLIGHT_ID_REQ, 'error')
            return render_template('seriouserror.html'), 406

        passengers = fl.getFlightInfo(flight, pass_form, flight_key)

    return render_template('passengercontact.html', form=pass_form, passengers=passengers[0], primes=passengers[1]), 200


# Get all flights for one day
# Return in JSON format
@app.route("/getdayflights/<strdate>/<airportcode>", methods=['GET'])
def getdayflights(strdate, airportcode):
    # Scrub the input date.
    fl = Flights(db)
    try:
        today = datetime.strptime(strdate, '%m%d%Y')
        today = datetime.date(today)
        tomorrow = today + timedelta(days=1)
        flightList = fl.get_day_flights(airportcode=airportcode, startdate=today, enddate=tomorrow)
    except ValueError:
        msg = f'{strdate} is invalid'
        flash(msg, 'error')
        return render_template('seriouserror.html'), 406

    return flightList, 201

# Find all purchasedflights for a customer
@app.route("/findmyride", methods=['GET'])
def findmyride():
    ride_form = FindMyRide()           # Get the form template
    args = request.args.to_dict()       # Get the params
    phone = ""
    email = ""
    if "phone" in args:
        phone = args['phone']

    if "email" in args:
        email = args['email']

    if phone != "" or email != "":
        customer = Customer(db)
        flight_data = customer.get_transaction(scrub_phone(phone), email)
        if len(flight_data) == 0:
            return render_template('findmyride.html', form=ride_form), 204
        else:
            flight_dict= {"flights": flight_data}
            json_data = json.dumps(flight_dict)
            return json_data, 201

    # Tell the html that there are no rides to display
    findmyride.prime_available_seats = 0
    findmyride.pass_available_seats = 0

    return render_template('findmyride.html', form=ride_form), 200

# Get one flight by primary key
@app.route("/getoneflight/<primarykey>", methods=['GET'])
def getoneflight(primarykey):
    fl = fl(db)
    flight = fl.get_one_flight(primarykey)

    return flight, 201

print(f"Starting INDYCAF WARBIRDS: {__name__}")
if __name__ == "__main__":
    port = os.getenv("PORT")
    if port is None:
        print("PORT environment variable missing.\nSetting port to 3000")
        port = 3000

    print(f"Warbird Booking started on port: {port}")
    # fm = FlaskMail(app)
    # fm.send_message("Warbirds Started", "jimolivi@icloud.com", "Warbirds program Started")
    # app.config.update['DEBUG'] = True
    app.run()
    print("Warbirds Rides Booking System ended.")
