from __future__ import print_function


from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

start_date = datetime.utcnow().date()
end_date = start_date + timedelta(days=30)
CALENDAR_ID = 'primary'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def getDates():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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


