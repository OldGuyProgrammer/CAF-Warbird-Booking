#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Volunteer Object
# The constructor will try and read a volunteer record from the database. If one is not
# found, a dummy Volunteer object will be created.
# The update method will try and read one from the database. If that record is not found, then
# a new record will be added.
#
#   Jim Olivi 2022
#

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
from globals import globals as gl, signals as sigs
from flaskmail import FlaskMail
from security import Security
import asyncio

# The volunteer object is a specific CAF volunteer.
# Potential customers and riders do not need to log in at this time.

class Volunteer(UserMixin):
    def __init__(self, db, user_id):
# Use the user_id (colonel number) to try and read a record.
# If a record is read, return the colonel number. If no record is found, return None

        self.db = db

# Set up an empty person record
        self.volunteer = {}
        self.volunteer[gl.DB_COLONEL_NUMBER] = user_id
        self.volunteer[gl.DB_ACTIVE] = False
        self.volunteer[gl.DB_FIRST_NAME] = ""
        self.volunteer[gl.DB_LAST_NAME] = ""
        self.volunteer[gl.DB_PASSWORD] = ""
        self.volunteer[gl.DB_ACTIVE] = False
        self.volunteer[gl.DB_AUTHENTICATED] = False

            # Signal to the front end to collect data for a new volunteer record.
        self.volunteer[gl.DB_VOLUNTEER_ON_FILE] = "NEW"
        if user_id is not None:
            person = self.db.get_person(user_id)
            if person is not None:
                self.volunteer = person
                if "_id" in person:
                    self.volunteer[gl.DB_COLONEL_NUMBER] = person["_id"]

                    # Signal to the front end to update a record already on file..
                self.volunteer[gl.DB_VOLUNTEER_ON_FILE] = "UPDATE"

    def person_data(self):
        scrubbed_vol = {
            gl.DB_COLONEL_NUMBER: self.volunteer[gl.DB_COLONEL_NUMBER],
            gl.DB_FIRST_NAME: self.volunteer[gl.DB_FIRST_NAME],
            gl.DB_LAST_NAME: self.volunteer[gl.DB_LAST_NAME],
            gl.DB_VOLUNTEER_ON_FILE: self.volunteer[gl.DB_VOLUNTEER_ON_FILE],
            gl.DB_CREW_POSITIONS: self.volunteer[gl.DB_CREW_POSITIONS]
        }
        return scrubbed_vol

    # Check if the volunteer (user id or Colonel Number) is already on the database.
    # If not, add a new volunteer to the database, encrypting the password
    # If update, hash the new password and update the fields sent

    def update_volunteer(self, app, volunteer_form, **kwargs):
# Filter out the blank crew positions.
        crew_positions = []
        for key, value in kwargs.items():
            if key == gl.DB_CREW_POSITIONS:
                crew_positions = [vol for vol in value if "" != vol]
# See if we create a new person record, or update an old one.
        old_person = self.db.get_person(volunteer_form[gl.DB_COLONEL_NUMBER].data)
        sec = Security(app)
        if old_person is None:
# Copy the fields we want to keep.
            self.volunteer["_id"] = volunteer_form[gl.DB_COLONEL_NUMBER].data
            self.volunteer[gl.DB_FIRST_NAME] = volunteer_form[gl.DB_FIRST_NAME].data
            self.volunteer[gl.DB_LAST_NAME] = volunteer_form[gl.DB_LAST_NAME].data
            self.volunteer[gl.DB_ACTIVE] = True
            self.volunteer[gl.DB_AUTHENTICATED] = True
            self.volunteer[gl.DB_CREW_POSITIONS] = crew_positions

            # Add a new volunteer to the database
            self.volunteer[gl.DB_PASSWORD] = sec.make_password(volunteer_form[gl.DB_PASSWORD].data)

            res = self.db.add_volunteer(self.volunteer)
            if res == sigs.database_op_success:
                msg = "New Volunteer Added to Database.\n"
                msg = msg + f"Name: {self.volunteer[gl.DB_FIRST_NAME]} {self.volunteer[gl.DB_LAST_NAME]}\n"
                msg = msg + f"Col #: {self.volunteer[gl.DB_COLONEL_NUMBER]}"
                # fm = FlaskMail(app)
                # fm.send_message("New Volunteer added", "jimolivi@icloud.com", msg)
            return res
        else:
            # Update the volunteer record
            if sec.authenticate_user(old_person[gl.DB_PASSWORD], volunteer_form[gl.DB_PASSWORD].data):
                if gl.DB_NEW_PASSWORD in volunteer_form and volunteer_form[gl.DB_NEW_PASSWORD].data != "":
                    # Hash new password.
                    volunteer_form[gl.DB_PASSWORD] = sec.make_password(volunteer_form[gl.DB_NEW_PASSWORD])
                    volunteer_form.pop(gl.DB_NEW_PASSWORD)

                self.volunteer[gl.DB_FIRST_NAME] = volunteer_form[gl.DB_FIRST_NAME].data
                self.volunteer[gl.DB_LAST_NAME] = volunteer_form[gl.DB_LAST_NAME].data
                self.volunteer[gl.DB_CREW_POSITIONS] = crew_positions
                self.db.update_volunteer(old_person["_id"], self.volunteer)
                msg = "Volunteer Updated.\n"
                msg = msg + f"Name: {self.volunteer[gl.DB_FIRST_NAME]} {self.volunteer[gl.DB_LAST_NAME]}\n"
                msg = msg + f"Col #: {self.volunteer[gl.DB_COLONEL_NUMBER]}"
                flash(msg, "message")
            else:
                msg = "Volunteer Not Updated.\nTry Again..."
                flash(msg, "message")

            return sigs.success

    @property
    def firstname(self):
        return self.volunteer[gl.DB_FIRST_NAME]

    @property
    def lastname(self):
        return self.volunteer[gl.DB_LAST_NAME]


    def login_volunteer(self, login_form, app):
        sec = Security(app)
        # Authenticate the user, password must equal.

        vol = self.db.get_person(login_form.userid.data, gl.DB_PASSWORD)
        if vol is None:
            flash(gl.MSG_LOGIN_FAILED, "error")
            flash(gl.MSG_CONTACT_ADMIN, "error")
            return sigs.failure
        if sec.authenticate_user(vol[gl.DB_PASSWORD], login_form.password.data):
            query = {gl.DB_AUTHENTICATED: True}
            self.db.update_volunteer(self.volunteer[gl.DB_COLONEL_NUMBER], query)
            return sigs.success
        else:
            flash(gl.MSG_LOGIN_FAILED, "error")
            flash(gl.MSG_CONTACT_ADMIN, "error")
            return sigs.failure


    @property
    def is_authenticated(self):
        if gl.DB_AUTHENTICATED in self.volunteer:
            return self.volunteer[gl.DB_AUTHENTICATED]
        else:
            return False

    def is_anonymous(self):
        return False


    def is_active(self):
        if gl.DB_ACTIVE in self.volunteer:
            return self.volunteer[gl.DB_ACTIVE]
        else:
            return False

    # Return the primary key of the user trying to use the system
    # In most cases, this will be the user's colonel number.
    # In all cases, the primary key of the user is the one passed from Flask

    def get_id(self):
        return self.volunteer[gl.DB_COLONEL_NUMBER]

#
# def get(self):
#     return self.volunteer[gl.DB_RECORD_KEY]

async def get_crew(db, crew_select):
    crew_array_db = db.getcrew(crew_select)
    crew_model = []
    for crew in crew_array_db:
        id = crew['_id']
        first_name = crew[gl.DB_FIRST_NAME]
        last_name = crew[gl.DB_LAST_NAME]
        crew_obj = (id, f'{first_name} {last_name}')
        crew_model.append(crew_obj)

    return crew_model

    # Retrieve requested lists from the database
async def getLists(db) -> None:

    task_pilots = asyncio.create_task(get_crew(db, gl.DB_PILOT))
    task_crew_chiefs = asyncio.create_task(get_crew(db, gl.DB_CREWCHIEF))
    task_loadmasters = asyncio.create_task(get_crew(db, gl.DB_LOAD_MASTER))

    # ac = ap(db)
    # task_airplanes = asyncio.create_task(ac.get_air_planes())

    pilots = await task_pilots
    crew_chiefs = await task_crew_chiefs
    loadmasters = await task_loadmasters
    # airplanes = await task_airplanes

    return [pilots, crew_chiefs, loadmasters]


