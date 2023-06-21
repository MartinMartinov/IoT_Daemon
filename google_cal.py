# Google libraries
import httplib2
import googleapiclient.discovery as discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Other
import datetime
import os

### Access Google Calendar ###
class GoogleCal():
    def __init__(self):
        self.SCOPES             = "https://www.googleapis.com/auth/calendar.readonly"
        self.CLIENT_SECRET_FILE = "/home/martinov/IoT_Daemon/client_secret_google_calendar.json"
        self.APPLICATION_NAME   = "Google Calendar - Raw Python"

    def get_credentials(self):
        home_dir = os.path.expanduser("~")
        credential_dir = os.path.join(home_dir, ".credentials")
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,"calendar-python-quickstart.json")
     
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print("Storing credentials to " + credential_path)
        return credentials

    def connect(self):
        self.credentials = self.get_credentials()
        self.http        = self.credentials.authorize(httplib2.Http())
        self.service     = discovery.build('calendar', 'v3', http=self.http)

    # Retrieve the events for today and fitler for work
    def get_start_today(self, names):
        eventsResult = self.service.events().list(
            calendarId='primary',
            timeMin=datetime.date.today().isoformat() + "T00:00:00Z",
            timeMax=(datetime.date.today()+datetime.timedelta(1)).isoformat() + "T00:00:00Z",
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = eventsResult.get('items', [])
        
        datetimes = {}
        for event in events:
            if 'summary' in event:
                for name in names:
                    if event['summary'] == name:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        datetimes[name] = datetime.datetime.fromisoformat(start)
        return datetimes