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

        self.db = db

        fields = [
            gl.DB_RECORD_KEY,
            gl.DB_FIRST_NAME,
            gl.DB_LAST_NAME,
            gl.DB_ADMIN,
            gl.DB_PILOT,
            gl.DB_CREWCHIEF,
            gl.DB_LOAD_MASTER
        ]
        if user_id is None:
            # Set up an empty person record: The volunteer is not on file.
            self.volunteer = {}
            self.volunteer[gl.DB_ACTIVE] = False
            self.volunteer[gl.DB_RECORD_KEY] = ""
            self.volunteer[gl.DB_FIRST_NAME] = ""
            self.volunteer[gl.DB_LAST_NAME] = ""
            self.volunteer[gl.DB_PASSWORD] = ""
            self.volunteer[gl.DB_ADMIN] = False
            self.volunteer[gl.DB_ACTIVE] = False
            self.volunteer[gl.DB_AUTHENTICATED] = False
            self.volunteer[gl.DB_PILOT] = False
            self.volunteer[gl.DB_CREWCHIEF] = False
            self.volunteer[gl.DB_LOAD_MASTER] = False
        else:
            # Is this person on file?
            # KEY_ID is the UserID and should be the colonel number
            person = self.db.get_person(user_id, fields)
            if person is not None:
                # Do we have update data?
                self.volunteer = person
                self.volunteer[gl.DB_RECORD_KEY] = person[gl.DB_RECORD_KEY]
                self.volunteer[gl.DB_ACTIVE] = True
                self.volunteer[gl.DB_AUTHENTICATED] = True
            else:
                # Set up an empty person record: The volunteer is not on file.
                self.volunteer = {}
                self.volunteer[gl.DB_ACTIVE] = False
                self.volunteer[gl.DB_RECORD_KEY] = ""
                self.volunteer[gl.DB_FIRST_NAME] = ""
                self.volunteer[gl.DB_LAST_NAME] = ""
                self.volunteer[gl.DB_PASSWORD] = ""
                self.volunteer[gl.DB_ADMIN] = False
                self.volunteer[gl.DB_ACTIVE] = False
                self.volunteer[gl.DB_AUTHENTICATED] = False
                self.volunteer[gl.DB_PILOT] = False
                self.volunteer[gl.DB_CREWCHIEF] = False
                self.volunteer[gl.DB_LOAD_MASTER] = False

    @property
    def person_data(self):
        return self.volunteer

    # Check if the volunteer (user id or Colonel Number) is already on the database.
    # If not, add a new volunteer to the database, encrypting the password
    # If update, hash the new password and update the fields sent

    def update_volunteer(self, app, new_volunteer):
        if new_volunteer[gl.DB_RECORD_KEY] == "":
            return sigs.userid_required
        sec = Security(app)
        self.volunteer = {key: value for key, value in new_volunteer.items() if key != gl.DB_RECORD_KEY}
        new_volunteer[gl.DB_ACTIVE] = True
        fields = [
            gl.DB_FIRST_NAME,
            gl.DB_LAST_NAME,
            gl.DB_PASSWORD
        ]
        old_person = self.db.get_person(new_volunteer[gl.DB_RECORD_KEY], fields)
        if old_person is None:
            # Add a new volunteer to the database
            new_volunteer[gl.DB_PASSWORD] = sec.make_password(new_volunteer[gl.DB_PASSWORD])
            # Save UserID because it's changed in the database routine.
            user_id = new_volunteer[gl.DB_RECORD_KEY]
            res = self.db.add_volunteer(new_volunteer)
            if res == sigs.database_op_success:
                msg = "New Volunteer Added to Database.\n"
                msg = msg + f"Name: {new_volunteer[gl.DB_FIRST_NAME]} {new_volunteer[gl.DB_LAST_NAME]}\n"
                msg = msg + f"Col #: {user_id}"
                fm = FlaskMail(app)
                flash("Volunteer Added.", "message")
                flash(f"{request.form[gl.DB_FIRST_NAME]} {request.form[gl.DB_LAST_NAME]} added.", 'message')
                fm.send_message("New Volunteer added", "jimolivi@icloud.com", msg)
            return res
        else:
            # Update the volunteer record
            if sec.authenticate_user(old_person[gl.DB_PASSWORD], new_volunteer[gl.DB_PASSWORD]):
                if gl.DB_NEW_PASSWORD in new_volunteer and new_volunteer[gl.DB_NEW_PASSWORD] != "":
                    # Hash new password.
                    new_volunteer[gl.DB_PASSWORD] = sec.make_password(new_volunteer[gl.DB_NEW_PASSWORD])
                    new_volunteer.pop(gl.DB_NEW_PASSWORD)
                else:
                    new_volunteer.pop(gl.DB_NEW_PASSWORD)
                    new_volunteer.pop(gl.DB_PASSWORD)

                user_id = new_volunteer[gl.DB_RECORD_KEY]
                new_volunteer.pop(gl.DB_RECORD_KEY)
                self.db.update_volunteer(user_id, new_volunteer)
                msg = "Volunteer Updated.\n"
                msg = msg + f"Name: {new_volunteer[gl.DB_FIRST_NAME]} {new_volunteer[gl.DB_LAST_NAME]}\n"
                msg = msg + f"Col #: {user_id}"
                flash("Volunteer Updated.", "message")
                flash(f"{request.form[gl.DB_FIRST_NAME]} {request.form[gl.DB_LAST_NAME]} updated.", 'message')
                fm = FlaskMail(app)
                fm.send_message("Volunteer Updated", "jimolivi@icloud.com", msg)
                return sigs.success
            else:
                flash(gl.MSG_LOGIN_FAILED, "error")
                flash(gl.MSG_CONTACT_ADMIN, "error")
                return sigs.failure

            res = self.db.update_volunteer(self.volunteer[gl.DB_RECORD_KEY], volunteer)
            if res == sigs.database_op_success:
                msg = "Volunteer Record Updated.\n"
                msg = msg + f"Name: {old_person[gl.DB_FIRST_NAME]} {old_person[gl.DB_LAST_NAME]}\n"
                msg = msg + f"Col #: {volunteer[gl.DB_RECORD_KEY]}"
                flash(msg, "message")
                fm = FlaskMail(app)
                fm.send_message("Volunteer record Updated", "jimolivi@icloud.com", msg)

        return res

    @property
    def firstname(self):
        return self.volunteer[gl.DB_FIRST_NAME]

    @property
    def lastname(self):
        return self.volunteer[gl.DB_LAST_NAME]


    def login_volunteer(self, login_form, app):
        sec = Security(app)
        # Authenticate the user, password must equal.

        vol = self.db.get_person(login_form.userid.data, [gl.DB_PASSWORD])
        if vol is None:
            flash(gl.MSG_LOGIN_FAILED, "error")
            flash(gl.MSG_CONTACT_ADMIN, "error")
            return sigs.failure
        if sec.authenticate_user(vol[gl.DB_PASSWORD], login_form.password.data):
            query = {gl.DB_AUTHENTICATED: True}
            self.db.update_volunteer(self.volunteer[gl.DB_RECORD_KEY], query)
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
        return self.volunteer[gl.DB_RECORD_KEY]

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


