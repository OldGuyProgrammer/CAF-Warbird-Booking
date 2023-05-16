#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Manage customer/passenger information
#
#   Jim Olivi 2022
#

from globals import signals as s, globals as gl

class Customer:

    def __init__(self, db):
        self.db = db


    def get_transaction(self, phone, email):

        all_flights = []
        query = {gl.DB_PHONE_NUMBER: phone, gl.DB_EMAIL: email}
        transactions = self.db.get_transactions(query)
        for transaction in transactions:
            flight = self.db.get_one_flight(transaction[gl.DB_FLIGHT_ID])
            info = {}
            info.update({gl.DB_FLIGHT_ID: transaction[gl.DB_FLIGHT_ID]})
            info.update({gl.DB_TRANSACTION_ID: transaction[gl.DB_TRANSACTION_ID]})
            info.update({gl.DB_AIRPORT_CITY: flight[gl.DB_AIRPORT_CITY]})
            info.update({gl.DB_AIRPORT_NAME: flight[gl.DB_AIRPORT_NAME]})
            info.update({gl.DB_FLIGHT_TIME: flight[gl.DB_FLIGHT_TIME]})
            all_flights.append(info)

        return all_flights

    def get_reservation(self, flight_key, transaction_key):
        reservation = self.db.get_reservation(flight_key, transaction_key)
        return reservation
