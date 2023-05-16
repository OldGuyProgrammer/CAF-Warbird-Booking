#
# Indiana Wing Commemorative Air Force
#     Warbird Rides Management System
#         Server side
#         Google Services
#
#   Jim Olivi 2022
#
# Google Mail Merge Sample Project
#
# Copied from the Google Tutorials.

import os
import os.path

import io
from google.auth.transport.requests import Request
from google.auth.exceptions import TransportError, GoogleAuthError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flask import render_template, flash
from globals import globals as gl

# Get Docs template
docs_file_id = os.getenv('DOCS_FILE_ID')
# print(f"File ID: {docs_file_id}")

# authorization constants
scopes = (os.getenv('SCOPES_DRIVE'), os.getenv('SCOPES_DOCS'))
# print(f"Scopes: {scopes}")

class GoogleServices:
    def __init__(self, manifest_data):
        self.manifest = None
        creds = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
# If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './static/json/credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('docs', 'v1', credentials=creds)

            # Retrieve the document contents from the Docs service.
            self.manifest = service.documents().get(documentId=docs_file_id).execute()

            # print('The title of the document is: {}'.format(document.get('title')))
        except HttpError as err:
            print(err)
            raise Exception(gl.MSG_GOOGLE_MAIL_MERGE_FAILURE)

# Fill in entire structure. If data is blank, it will be blanked on the mail merge
# Crew Section
        crew = manifest_data[0]
        merge = {}
        merge[gl.MM_PIC] = crew[gl.MN_PIC]
        if crew[gl.MN_SIC] != "":
            merge[gl.MM_SIC] = crew[gl.MN_SIC]
        else:
            merge[gl.MM_SIC] = "___________"
        if crew[gl.MN_CREW_CHIEF_NAME] != "":
            merge[gl.MM_ENG] = crew[gl.MN_CREW_CHIEF_NAME]
        else:
            merge[gl.MN_CREW_CHIEF_NAME] = "____________"
        merge[gl.MN_LOAD_MASTER_NAME] = crew[gl.MN_LOAD_MASTER_NAME]

# Header Section
        headers = manifest_data[2]
        flight_time = str(headers[gl.DB_FLIGHT_TIME])
        flight_date = flight_time.split()[0]    # Pull out full date
        # parts = flight_date.split("-")
        # formatted_date = parts[1] + "/" + parts[2] + "/" + parts[0]
        merge[gl.MM_AIRCRAFT_TYPE] = headers[gl.DB_AIRCRAFT_TYPE]
        merge["N"] = headers[gl.DB_N_NUMBER]
        merge[gl.MM_DEPART] = headers[gl.DB_AIRPORT_CODE]
        if headers[gl.DB_AIRPORT_CODE] != "":
            merge[gl.MM_ARRIVAL] = headers[gl.DB_AIRPORT_CODE]
        else:
            merge[gl.MM_ARRIVAL] = "_________"

# Signature/Passenger Section
        passengers = manifest_data[1]
        line = 1
        str_line = str(line)
        name = "NAME_" + str_line
        merge[name] = crew[gl.MN_PIC]
        col = "COL_" + str_line
        merge[col] = crew[gl.MN_PIC_ID]
        pos = "POS_" + str_line
        merge[pos] = gl.MM_PIC
        date = "DATE_" + str_line
        merge[date] = flight_date
        if crew[gl.MN_SIC] != "":
            line += 1
            str_line = str(line)
            name = "NAME_" + str_line
            merge[name] = crew[gl.MN_SIC]
            col = "COL_" + str_line
            merge[col] = crew[gl.MN_SIC]
            pos = "POS_" + str_line
            merge[pos] = gl.MN_SIC
            date = "DATE_" + str(line)
            merge[date] = flight_date
        if crew[gl.MN_CREW_CHIEF_NAME] != "":
            line += 1
            str_line = str(line)
            name = "NAME_" + str(line)
            merge[name] = crew[gl.MN_CREW_CHIEF_NAME]
            col = "COL_" + str_line
            merge[col] = crew[gl.MN_CREW_CHIEF_ID]
            pos = "POS_" + str_line
            merge[pos] = gl.MM_ENG
            date = "DATE_" + str(line)
            merge[date] = flight_date
        if crew[gl.MN_LOAD_MASTER_NAME] != "":
            line += 1
            str_line = str(line)
            name = "NAME_" + str(line)
            merge[name] = crew[gl.MN_LOAD_MASTER_NAME]
            col = "COL_" + str_line
            merge[col] = crew[gl.MN_LOAD_MASTER_ID]
            pos = "POS_" + str_line
            merge[pos] = gl.MM_LOAD_MASTER
            date = "DATE_" + str(line)
            merge[date] = flight_date

        for passenger in passengers:
            line += 1
            str_line = str(line)
            name = "NAME_" + str_line
            merge[name] = passenger[1]
            col = "COL_" + str_line
            merge[col] = ""
            pos = "POS_" + str_line
            if passenger[1]:        # Is this a prime seat
                merge[pos] = gl.MM_PRIME
            else:
                merge[pos] = ""
            date = "DATE_" + str_line
            merge[date] = flight_date

        if line <= 11:
            for n in range(11 - line):
                line += 1
                str_line = str(line)
                name = "NAME_" + str_line
                merge[name] = ""
                date = "DATE_" + str_line
                merge[date] = ""
                col = "COL_" + str_line
                merge[col] = ""
                pos = "POS_" + str_line
                merge[pos] = ""

        dict_data = dict(merge)

        """Copies letter template document using Drive API then
            returns file ID of (new) copy.
            Google copies the manifest form and returns the new ID.
        """
        try:
            body = {'name': 'Merged form letter (%s)' % docs_file_id}
            service = build('drive', 'v2', credentials=creds)
            copy_id = service.files().copy(body=body, fileId=docs_file_id, fields='id').execute().get('id')
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise Exception(gl.MSG_GOOGLE_MAIL_MERGE_FAILURE)
        # print(dict_data)

        context = dict_data.items()
        # Structure that defines the mail merge
        reqs = [{'replaceAllText': {
            'containsText': {
                'text': '{{%s}}' % key,
                'matchCase': False,
            },
            'replaceText': replacement_text,
        }} for key, replacement_text in context]
        docs = build('docs', 'v1', credentials=creds)

# Download the new merged file
        try:
            docs.documents().batchUpdate(body={'requests': reqs}, documentId=copy_id, fields='').execute()
            req = service.files().export_media(fileId=copy_id, mimeType="application/pdf")
            manifest_file = io.BytesIO()
            downloader = MediaIoBaseDownload(manifest_file, req)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            self.manifest = manifest_file.getvalue()

        except HttpError as error:
            print(f'An error occurred retrieving merged document: {error}')
            raise Exception(gl.MSG_GOOGLE_MAIL_MERGE_FAILURE)

# Scrub the manifest data, then return the downloadable page.
    def get_manifest(self):

        return self.manifest


