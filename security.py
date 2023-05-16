#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Security Module
#
#   Jim Olivi 2002
#

from flask import session
from flask_bcrypt import Bcrypt

class Security:

    def __init__(self, app):
        self.bcrypt = Bcrypt(app)
    @property
    def get_user_id(self):
        return session.get('_user_id')

    def check_password(self, pwd_from_database, pwd_from_user):
        # Check the password
        return self.bcrypt.check_password_hash(pwd_from_database, pwd_from_user)

    def make_password(self, password):
        return self.bcrypt.generate_password_hash(password)

    def authenticate_user(self, database_password, login_password):
        if self.check_password(database_password, login_password):
            return True
        else:
            return False



