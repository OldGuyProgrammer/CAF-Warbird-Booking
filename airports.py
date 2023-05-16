#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Get Airport Info
#
#   Jim Olivi 2022
#

from dotenv import load_dotenv
from pathlib import Path
import requests
import os
from string import Template
from globals import globals as gl

class airports:
    def __init__(self):
        pass

    def get_airport_info(airport_code):
        # env_path = Path('.') / '.env'
        # load_dotenv(env_path)

        airport_code = airport_code.upper()
        try:
            airport_code_url_template = Template(os.getenv('AIRPORT_CODE_URL'))
            airport_code_api_key = os.getenv("AIRPORT_CODE_APIKEY")
        except KeyError:
            print(gl.MSG_AIRPORT_API_KEY_PROBLEM)
            return "Airport name not IATA complient."
        except:
            print(gl.MSG_GET_IATA_FAILED)
            return "Airport name not IATA complient."
        else:
            airport_code_url = airport_code_url_template.substitute(AIRPORTCODE=airport_code)
            response = requests.get(airport_code_url,
                                    params={"language": "en-US"},
                                    headers={"apiKey": airport_code_api_key, })

            if response.status_code == 200:
                airport = response.json()
                if airport['results_retrieved'] == 0:
                    return "Airport name not IATA complient."
                else:
                    airport_name = airport['locations'][0]['name']
                    airport_city = airport['locations'][0]['city']['name']
                    airport_info = {
                        "name": airport_name,
                        "city": airport_city
                    }
                    # print(airport_info)
                    return airport_info
            return
