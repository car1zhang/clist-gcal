#!/usr/bin/env python3

import requests
import re
import os.path
import datetime
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def fetch_contests():
    api_url = 'https://clist.by/api/v4/contest/?upcoming=true&limit=1000'
    headers = {
        'Authorization': f'ApiKey {os.getenv("CLIST_USERNAME")}:{os.getenv("CLIST_API_KEY")}'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            atcoder_contests = [contest for contest in data['objects'] if contest['resource'] == 'atcoder.jp' and bool(re.search(r'a(b|r|g)c', contest['href']))]
            codeforces_contests = [contest for contest in data['objects'] if contest['resource'] == 'codeforces.com' and bool(re.search(r'Round', contest['event']))]
            leetcode_contests = [contest for contest in data['objects'] if contest['resource'] == 'leetcode.com']
            dmoj_contests = [contest for contest in data['objects'] if contest['resource'] == 'dmoj.ca']

            all_contests = atcoder_contests + codeforces_contests + dmoj_contests + leetcode_contests
            return all_contests
        else:
            print(f'Failed to fetch data. Status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

def get_calendar_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                # If refresh fails, we might need to re-authenticate
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        open('token.json', 'w').write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(service):
    try:
        now = datetime.datetime.now().isoformat() + 'Z'
        events = service.events().list(calendarId='primary', timeMin=now, singleEvents=True).execute()
        return events.get('items', [])
    
    except Exception as e:
        print(f'An error occurred: {str(e)}')

def add_contest_to_calendar(service, contest):
    contest_name = f'{contest['resource'].upper()} - {contest['event']}'
    try:
        event = {
            'summary': contest_name,
            'description': f'{int(contest['duration'] / 3600)}h {int((contest['duration'] % 3600) / 60)}m - {contest['href']}\n\nCLIST_CONTEST',
            'start': {
                'dateTime': contest['start'],
                'timeZone': 'Africa/Abidjan',
            },
            'end': {
                'dateTime': contest['end'],
                'timeZone': 'Africa/Abidjan',
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        
    except Exception as e:
        print(f'An error occurred: {str(e)}')

    print(f'\033[95m{contest_name}\033[0m - \033[94m{event["htmlLink"]}\033[0m')

def remove_contest_from_calendar(service, event):
    if bool(re.search(r'CLIST_CONTEST', event.get('description', ''))):
        print(f'\033[91mRemoving {event.get('summary', '')} from calendar.\033[0m')
        service.events().delete(calendarId='primary', eventId=event.get('id', '')).execute()

def clear_calendar(service):
    try:
        now = datetime.datetime.now().isoformat() + 'Z'
        events = service.events().list(calendarId='primary', timeMin=now).execute()
        for event in events['items']:
            remove_contest_from_calendar(service, event)
        print('\033[92mCalendar cleared.\033[0m')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

if __name__ == '__main__':
    service = get_calendar_service()

    to_clear = input('Clear calendar? (y/N): ')
    if to_clear == 'y':
        clear_calendar(service)

    contests = fetch_contests()
    events = get_events(service)

    for contest in contests:
        contest_name = f'{contest['resource'].upper()} - {contest['event']}'
        if not any(event['summary'] == contest_name for event in events):
            add_contest_to_calendar(service, contest)
    print('\033[92mAll contests added to calendar.\033[0m')
