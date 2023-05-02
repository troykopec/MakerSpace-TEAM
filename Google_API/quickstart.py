from __future__ import print_function

from flask import flash

from datetime import datetime, timedelta
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

import importlib
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

app = importlib.import_module('app')

eastern = pytz.timezone('US/Eastern')
utc_now = datetime.utcnow()
eastern_now = utc_now.replace(tzinfo=pytz.utc).astimezone(eastern)
start_date = eastern_now.date()

end_date = start_date + timedelta(days=30)
CALENDAR_ID = 'primary'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']




def getDates():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        days_events = {}
        for i in range((end_date - start_date).days + 1):
            date = start_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%dT%H:%M:%S-00:00')
            start_of_day = datetime.combine(date, datetime.min.time()).isoformat() + 'Z'
            end_of_day = datetime.combine(date, datetime.max.time()).isoformat() + 'Z'

            events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=start_of_day,
                                                timeMax=end_of_day, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            days_events[date_str] = events
        
        
        return days_events
        
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        

def deleteDate(event_id):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        
def deleteDateInTimeframe(start_time, end_time):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        query_params = {
            'timeMin': start_time,
            'timeMax': end_time,
            'singleEvents': True,
            'orderBy': 'startTime',
        }
        events_result = service.events().list(calendarId=CALENDAR_ID, **query_params).execute()
        events = events_result.get('items', [])
        count = 0
        if not events:
            flash(f'No events found between the specified times: ({start_time}) -> ({end_time})')
        else:
            for event in events:
                event_id = event["id"]
                app.delete_API_reservation_loop(event_id)
            flash("Time Slot(s) Removed Successfully!")
    except HttpError as error:
        print('An error occurred: %s' % error)
        


