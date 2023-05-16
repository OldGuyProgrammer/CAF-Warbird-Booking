#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Square Credit Card Services
#
#   Jim Olivi 2023
#
# Copied from the Square API examples.

# from square.client import Client
# import os
#
# client = Client(
#     access_token=os.environ['SQUARE_ACCESS_TOKEN'],
#     environment='sandbox-sq0idb-RT3u-HhCpNdbMiGg5aXuVg')
#
# result = client.locations.list_locations()
#
# if result.is_success():
#     for location in result.body['locations']:
#         print(f"{location['id']}: ", end="")
#         print(f"{location['name']}, ", end="")
#         print(f"{location['address']['address_line_1']}, ", end="")
#         print(f"{location['address']['locality']}")
#
# elif result.is_error():
#     for error in result.errors:
#         print(error['category'])
#         print(error['code'])
#         print(error['detail'])
