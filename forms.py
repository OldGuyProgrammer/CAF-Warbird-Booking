#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         forms module
#
#   Jim Olivi 2002
#

from globals import globals as gl
from wtforms import StringField, HiddenField, PasswordField,\
    BooleanField, IntegerField, DateTimeField, TelField, \
    SelectField, EmailField, validators, SubmitField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField

class Home(FlaskForm):
    is_authenticated = BooleanField()
    FirstName = StringField()
    LastName = StringField()

class LoginForm(FlaskForm):
    userid = StringField(gl.PR_COLONEL_NUMBER, [validators.InputRequired()], render_kw={'placeholder': gl.PR_COLONEL_NUMBER})
    password = PasswordField(gl.DB_PASSWORD, [validators.InputRequired()], render_kw={'placeholder': gl.PR_PASSWORD})
    next_url = HiddenField('Next_url')


class AddAircraft(FlaskForm):
    aircraft_name = StringField(gl.PR_AIRCRAFT_NAME, [validators.InputRequired()], render_kw={'placeholder': gl.PR_AIRCRAFT_NAME})
    aircraft_n_number = StringField(gl.DB_RECORD_KEY,
                                    [validators.InputRequired(),
             validators.Length(min=3, max=6),
             validators.Regexp('^\w+$', message=gl.MSG_N_NUMBER)],
                                    render_kw={'placeholder': gl.PR_AIRCRAFT_N_NUMBER})
    aircraft_type = StringField(gl.PR_AIRCRAFT_TYPE, [validators.InputRequired()],
                                render_kw={'placeholder': gl.PR_AIRCRAFT_TYPE})
    aircraft_image_file_name = FileField(gl.PR_AIRCRAFT_PHOTO )
    operational = BooleanField(gl.PR_AIRCRAFT_OPERATIONAL, render_kw={'checked': True})
    add_aircraft = SubmitField(gl.PR_ADD_AIRCRAFT)


class CreateFlightForm(FlaskForm):
    airport_code = StringField(gl.PR_IATA_CODE, [validators.InputRequired(), validators.Length(min=3, max=4,
                                message='IATA Codes can have 3 or 4 characters, the K is not required')],
                               render_kw={'placeholder': gl.PR_IATA_CODE, 'style': 'width: 15%'})
    airport_name = StringField(gl.PR_AIRPORT_NAME, render_kw={'placeholder': gl.PR_AIRPORT_NAME, 'style': 'width: 30%'})
    airport_city = StringField(gl.PR_AIRPORT_CITY, render_kw={'placeholder': gl.PR_AIRPORT_CITY, 'style': 'width: 30%'})
    flight_time = DateTimeField(gl.PR_FLIGHT_TIME, [validators.InputRequired()], format='%Y-%m-%dT%H:%M', render_kw={'type': 'datetime-local'})
    end_flight_time = DateTimeField(gl.PR_END_FLIGHT_TIME, [validators.InputRequired()], format='%Y-%m-%dT%H:%M', render_kw={'type': 'datetime-local'})
    premium_price = IntegerField(gl.PR_PRICE, default=0, render_kw={'placeholder': gl.PR_PRICE,'style': 'width: 50%'})
    passenger_price = IntegerField(gl.PR_PRICE, default=0, render_kw={'placeholder': gl.PR_PRICE,'style': 'width: 50%'})
    number_prime_seats = IntegerField(gl.PR_NUMBER_SEATS,default=0, render_kw={'placeholder': gl.PR_NUMBER_SEATS,'style': 'width: 50%'})
    number_pass_seats = IntegerField(gl.PR_NUMBER_SEATS, default=0, render_kw={'placeholder': gl.PR_NUMBER_SEATS,'style': 'width: 50%'})
    pilots = SelectField(label='pilots', id='pilots', choices=[], validate_choice=False)
    co_pilots = SelectField(label='co-pilots', id='co-pilots',  choices=[], validate_choice=False)
    crew_chiefs = SelectField(label='Crew Chiefs', id='crew_chiefs', choices=[], validate_choice=False)
    loadmasters = SelectField(label='Load Masters', id='loadmasters', choices=[], validate_choice=False)
    add_a_flight = SubmitField(gl.PR_ADD_A_FLIGHT)


class AddVolunteer(FlaskForm):
    record_id = StringField(gl.PR_COLONEL_NUMBER, [validators.InputRequired("Enter Colonel Number")],
                         render_kw={'placeholder': gl.PR_COLONEL_NUMBER, 'style': 'width: 25%'})
    FirstName = StringField(gl.PR_FIRST_NAME, [validators.InputRequired('Enter First Name')], render_kw={'placeholder': gl.PR_FIRST_NAME})
    LastName = StringField(gl.PR_LAST_NAME, [validators.InputRequired('Enter Last Name')], render_kw={'placeholder': gl.PR_LAST_NAME})
    password = PasswordField(gl.PR_PASSWORD, [validators.InputRequired('Password Required')], render_kw={'placeholder': gl.PR_PASSWORD})
    new_password = PasswordField(gl.PR_PASSWORD, render_kw={'placeholder': gl.PR_NEW_PASSWORD})
    admin = BooleanField(gl.PR_ADMIN)
    pilot = BooleanField(gl.PR_PILOT)
    crew_chief = BooleanField(gl.PR_CREWCHIEF)
    loadmaster = BooleanField(gl.PR_LOADMASTER)

class PassengerContact(FlaskForm):
    first_name = StringField(gl.PR_FIRST_NAME, [validators.InputRequired(gl.MSG_ENTER_NAME)], render_kw={'placeholder': gl.PR_FIRST_NAME})
    card_title = StringField('Flight Title Goes Here')
    last_name = StringField(gl.PR_FIRST_NAME, [validators.InputRequired(gl.MSG_ENTER_NAME)], render_kw={'placeholder': gl.PR_LAST_NAME})
    pass_email = EmailField(gl.PR_EMAIL, render_kw={'placeholder': gl.PR_EMAIL})
    pass_phone = TelField(gl.PR_PHONE, render_kw={'placeholder': gl.PR_PHONE})
    OKtoText = BooleanField(gl.PR_OK_TEXT)
    pass_addr = StringField(gl.PR_ADDRESS, render_kw={'placeholder': gl.PR_ADDRESS, 'class':'col-8'})
    pass_city = StringField(gl.PR_CITY, render_kw={'placeholder': gl.PR_CITY})
    state_province = SelectField('State/Province',  choices=[], validate_choice=False)
    pass_postal = StringField(gl.PR_POSTAL, render_kw={'placeholder': gl.PR_POSTAL})
    prime_seat_price = StringField()
    pass_seat_price = StringField()
    prime_name = StringField(gl.PR_PASS_NAME, render_kw={'placeholder': gl.PR_PASS_NAME, 'class': "prime_name"})
    passenger_name = StringField(gl.PR_PASS_NAME, render_kw={'placeholder': gl.PR_PASS_NAME, 'class': "passenger_name"})
    prime_available_seats = IntegerField()
    pass_available_seats = IntegerField()
    flight_id = StringField()
    total_prime_seats = StringField(gl.LBL_TOTAL, render_kw={'readonly': True, "tabindex": -1, 'style': 'width: 25%'})
    total_passenger_seats = StringField(gl.LBL_TOTAL, render_kw={'readonly': True, "tabindex": -1, 'style': 'width: 25%'})
    total_price = StringField(gl.LBL_TOTAL, render_kw={'style': 'width: 25%'})
    pay_for_flight = SubmitField(gl.PR_PAY_FOR_FLIGHT)
    paid_amount = HiddenField()


# Manifest: Choose Airport
class Manifest(FlaskForm):
    airport_codes = SelectField(label=gl.MN_CHOOSE_AIRPORT, id='airport_code',
                    choices=[], validate_choice=False)
    aircraft_type = StringField(label=gl.MN_AIRCRAFT_TYPE, render_kw={'style': 'width: 5%'})
    n_number = StringField(render_kw={'style': 'width: 7%'})
    departure_point = StringField(label=gl.MN_DEPARTURE_POINT, render_kw={'style': 'width: 7%'})
    arrival = StringField(label=gl.MN_ARRIVAL, render_kw={'style': 'width: 5%'})
    pilot_in_command = StringField(label=gl.MN_PIC, render_kw={'style': 'width: 10%'})
    co_pilot = StringField(label=gl.MN_SIC, render_kw={'style': 'width: 10%'})
    crew_chief = StringField(label=gl.MN_FLT_ENGINEER, render_kw={'style': 'width: 10%'})
    seat_position = StringField()
    flight_date = DateTimeField()

class FindMyRide(FlaskForm):
    pass_email = EmailField(gl.PR_EMAIL, render_kw={'placeholder': gl.PR_EMAIL})
    pass_phone = TelField(gl.PR_PHONE, render_kw={'placeholder': gl.PR_PHONE, 'type':'tel'})
    flight_id = StringField()
    prime_available_seats = IntegerField()
    pass_available_seats = IntegerField()

class FlightReport(FlaskForm):
    today = StringField()
    airport = StringField(gl.LBL_AIRPORT)
    aircraft = StringField(gl.LBL_AIRCRAFT)
    flightTime = StringField()
    pilotName = StringField()
    coPilotName = StringField()
    crewChiefName = StringField()
    loadMasterName = StringField()
    purchaser = StringField()
    phoneNumber = StringField()
    okToText = StringField()
    passengerName = StringField()
