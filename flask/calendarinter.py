from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
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
    return creds


import datetime

def delete_calendar_event(event_id, start_time_str):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    try:
        # First, try to delete the event by event ID
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except HttpError as e:
        if e.resp.status == 404:
            print("Event ID not found. Trying to find event by start time...")
            try:
                # If event ID not found, try to find the event by start time
                start_time = datetime.datetime.fromisoformat(start_time_str)
                end_time = start_time + datetime.timedelta(minutes=1)  # Adjust this as needed
                start_time_iso = start_time.isoformat()
                end_time_iso = end_time.isoformat()

                events_result = service.events().list(calendarId='primary', timeMin=start_time_iso, timeMax=end_time_iso).execute()
                events = events_result.get('items', [])
                if events:
                    # Found the event, delete it by its ID
                    event_id_to_delete = events[0]['id']
                    service.events().delete(calendarId='primary', eventId=event_id_to_delete).execute()
                    return True
                else:
                    print("Event not found by start time.")
                    return False
            except Exception as e:
                print(f"Error deleting event by start time: {e}")
                return False
        else:
            print(f"Error deleting event by ID: {e}")
            return False

def convert_to_iso8601(start_time_str):
    try:
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S%z")
        return start_time.isoformat()
    except ValueError:
        return None


