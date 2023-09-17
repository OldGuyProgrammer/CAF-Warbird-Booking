# #
# # Indiana Wing Commemorative Air Force
# #     Warbird Rides Management System
# #         Server side
# #         manifest
# #
# #   Collect manflight manifest information from the various databases
# #
# #   Jim Olivi 2022
# #
#
# from flights import Flights
# from globals import globals as gl, signals
# import asyncio
# from google_services import GoogleServices
# from google.auth.exceptions import TransportError, GoogleAuthError
#
# class Manifests:
#     def __init__(self, data_base):
#         self.db = data_base
#
#     async def get_crew_record(self, key) -> None:
#         fields = [
#             gl.DB_RECORD_KEY,
#             gl.DB_FIRST_NAME,
#             gl.DB_LAST_NAME,
#             gl.DB_ADMIN,
#             gl.DB_PILOT,
#             gl.DB_CREWCHIEF,
#             gl.DB_LOAD_MASTER
#         ]
#         crew = self.db.get_person(key, fields)
#         if crew is not None:
#             return (f'{crew[gl.DB_FIRST_NAME]} {crew[gl.DB_LAST_NAME]}')
#         else:
#             return ""
#
#     async def get_crew_info(self):
#
# # Set up the async tasks
#         pilot_id = self.flight[gl.DB_PILOT]
#         task_pilot = asyncio.create_task(self.get_crew_record(pilot_id))
#
#         co_pilot_id = self.flight[gl.DB_CO_PILOT]
#         task_co_pilot = asyncio.create_task(self.get_crew_record(co_pilot_id))
#
#         crew_chief_id = self.flight[gl.DB_CREWCHIEF]
#         task_crew_chief = asyncio.create_task(self.get_crew_record(crew_chief_id))
#
#         load_master_id = self.flight[gl.DB_LOAD_MASTER]
#         task_load_master = asyncio.create_task(self.get_crew_record(load_master_id))
#
# # wait for the Async tasks
#         co_pilot_name = await task_co_pilot
#         crew_chief_name = await task_crew_chief
#         load_master_name = await task_load_master
#         pilot_name = await task_pilot
#
#         crew = {
#             gl.MN_PIC: pilot_name,
#             gl.MN_PIC_ID: pilot_id,
#             gl.MN_SIC: co_pilot_name,
#             gl.MN_SIC_ID: co_pilot_id,
#             gl.MN_CREW_CHIEF_NAME: crew_chief_name,
#             gl.MN_CREW_CHIEF_ID: crew_chief_id,
#             gl.MN_LOAD_MASTER_NAME: load_master_name,
#             gl.MN_LOAD_MASTER_ID: load_master_id,
#         }
#         return crew
#
#     async def get_airplane_info(self, n_number):
#         airplane_record = self.db.get_one_airplane(n_number, gl.DB_N_NUMBER, gl.DB_AIRCRAFT_TYPE)
#         return airplane_record
#
#     def get_manifest_info(self, flight_id):
#         fl = Flights(self.db)
#         self.flight = fl.get_one_flight(flight_id)
#         airport_code = self.flight[gl.DB_AIRPORT_CODE]
#         crew = asyncio.run(self.get_crew_info())
#         airplane_info = asyncio.run(self.get_airplane_info(self.flight[gl.DB_N_NUMBER]))
#         manifest_header = {
#             gl.DB_N_NUMBER: self.flight[gl.DB_N_NUMBER],
#             gl.DB_FLIGHT_TIME: self.flight[gl.DB_FLIGHT_TIME],
#             gl.DB_AIRCRAFT_TYPE: airplane_info[gl.DB_AIRCRAFT_TYPE],
#             gl.DB_AIRPORT_CODE: airport_code,
#         }
#         passengers = []
#         if gl.DB_TRANSACTIONS in self.flight:
#             for transaction in self.flight[gl.DB_TRANSACTIONS]:
#                 if gl.DB_PRIME_SEATS in transaction:
#                     for seat in transaction[gl.DB_PRIME_SEATS]:
#                         passengers.append((1, seat))
#                 if gl.DB_VIP_SEATS in transaction:
#                     for seat in transaction[gl.DB_VIP_SEATS]:
#                         passengers.append((2, seat))
#
#         # print(passengers)
#         return crew, passengers, manifest_header
#
#     def get_manifest(self, flight_id):
#         manifest_data = self.get_manifest_info(flight_id)
#         try:
#             google = GoogleServices(manifest_data)
#             return signals.success, google.get_manifest()
#         except (TransportError, GoogleAuthError) as err:
#             msg = f"{gl.MSG_GOOGLE_MAIL_MERGE_FAILURE}: {err}"
#             print(msg)
#             return signals.failure, err
#         except:
#             return signals.failure, gl.MSG_GOOGLE_MAIL_MERGE_FAILURE
