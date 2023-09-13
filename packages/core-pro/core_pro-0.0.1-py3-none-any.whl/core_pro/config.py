import pickle
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


json_users = Path.home() / 'PycharmProjects/modeling/core_pro/content/client_secret.json'
google_services = {
    'sheets': {
        'scopes': ['https://www.googleapis.com/auth/spreadsheets'],
        'versions': 'v4',
        'json_path': json_users
    },
    'gmail': {
        'scopes': ['https://mail.google.com/'],
        'versions': 'v1',
        'json_path': json_users
    },
    'drive': {
        'scopes': ['https://www.googleapis.com/auth/drive'],
        'versions': 'v3',
        'json_path': json_users
    },
    'slides': {
        'scopes': ['https://www.googleapis.com/auth/presentations'],
        'versions': 'v1',
        'json_path': json_users
    }
}


class GoogleAuthentication:

    def __init__(self, service_type: str):
        """
        get google credentials
        :param service_type: 'sheets', 'gmail or 'drive' services
        :return: google credential
        """
        creds = None
        scopes, versions, json_paths = google_services[service_type].values()
        token_path = Path.home() / 'PycharmProjects/modeling/token'
        token_name = token_path / f'token_{service_type}.pickle'
        if not token_path.exists():
            token_path.mkdir(parents=True, exist_ok=True)
        if token_name.exists():
            creds = pickle.load(open(token_name, 'rb'))
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(json_paths, scopes)
                creds = flow.run_local_server(port=0)
            pickle.dump(creds, open(token_name, 'wb'))

        self.service = build(service_type, versions, credentials=creds)
