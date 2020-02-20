from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Optional, Dict, Any

from settings import CALENDER_ID

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar'
]


class GoogleCalnderHandler:
    def __init__(self) -> None:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self, result_num: int = 10) -> None:
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=result_num, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    def add_event(self,
                  title: str,
                  start_datetime: datetime.datetime,
                  end_datetime: datetime.datetime,
                  location: Optional[str],
                  ) -> Dict[str, Any]:
        event_param = {
            'summary': '予定1',
            'location': location,
            'start': {
                'dateTime': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Japan',
            },
        }
        return self.service.events().insert(
            calendarId=CALENDER_ID,
            body=event_param
        ).execute()


if __name__ == '__main__':
    handler = GoogleCalnderHandler()
    handler.get_events()
