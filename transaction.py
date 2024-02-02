#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Manage Flight Information
#
#   Jim Olivi 2024
#
import stat

from globals import globals as gl

class Transaction():

    def __init__(self, db, **kwargs):
        self.db = db
        self.purchaser_obj = kwargs

    def add_transaction(self):
        transaction_id = self.db.add_transaction(self.purchaser_obj)
        return str(transaction_id)