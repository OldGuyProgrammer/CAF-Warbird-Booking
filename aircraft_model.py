#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Aircraft Model
#
#   Jim Olivi 2022
#

class Aircraft:

    def __init__(self, db):
        self.db = db

# Reformat the aircraft dictionary for the database
    def AddAircraft(self, aircraft_form):
        aircraft_form['_id'] = aircraft_form.pop('aircraft_n_number')

        return self.db.AddAircraft(aircraft_form)

async def getAirPlanes(db):

    airplanes = db.getairplanes()
    airplane_array = []
    for air_plane in airplanes:
        airplane_value = f'{air_plane[0]}'
        airplane_image = f"{air_plane[1]}"
        airplane_name = f'{air_plane[0]} {air_plane[2]}'
        airplane_array.append((airplane_value, airplane_name, airplane_image))

    return airplane_array

def getOneAirplane(db, n_number):
    plane = db.get_one_airplane(n_number)
    if plane is None:
        return None;

    return plane
