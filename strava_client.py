from datetime import datetime
import requests
import time
import polyline
from os.path import exists
from os import environ
import json
import sys
import webbrowser
from builtins import input as askForInput
from activity_db_client import ActivityDBClient
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = environ.get("CLIENT_ID")
CLIENT_SECRET = environ.get("CLIENT_SECRET")


class StravaClient:
    def __init__(self, page_size = 30):
        self.page_size = page_size

        self.activity_db = ActivityDBClient()

        self.n_requests = 0
        self.start_time = time.time()
        if exists('./.credentials.json'):
            print("Using existing credentials", flush=True)
            with open('./.credentials.json', 'r') as input:
                self.credentials = json.load(input)
                if datetime.now().timestamp() > self.credentials["EXPIRES"]:
                    self._refresh_access_token()

        else:
            print("No credentials present. A web browser will open and ask for permission to read data from your Strava account. After authorizing the application, you will be directed to a nonexistant page with a 'code' in the URL")
            webbrowser.open(f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri=http://localhost&response_type=code&scope=read,activity:read_all")
            CODE = askForInput("Enter code from redirect URL:")
            self._get_access_token(CODE)


    def _refresh_access_token(self):
        print("Refreshing expired access token...", flush=True)
        self._authenticate({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": self.credentials["REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        })


    def _get_access_token(self, code):
        self._authenticate({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        })


    def _authenticate(self, payload):
        response = requests.post("https://www.strava.com/oauth/token", data=payload)
        if response.status_code != 200:
            print(response.json())
            sys.exit(1)

        data = response.json()
        credentials = {
            key: data[key] for key in ["access_token", "refresh_token", "expires_at"]
        }

        self.credentials = {
            "ACCESS_TOKEN": credentials["access_token"],
            "REFRESH_TOKEN": credentials["refresh_token"],
            "EXPIRES": credentials["expires_at"]
        }

        # Save for future use
        with open('./.credentials.json', 'w') as output:
            json.dump(self.credentials, output)


    def get_strava(self, url):
        headers = {
            "Authorization": f"Bearer {self.credentials['ACCESS_TOKEN']}"
        }
        response = requests.get(f"https://www.strava.com/api/v3/{url}", headers=headers)

        self.n_requests += 1

        if response.status_code != 200:
            print(response.status_code)
            print(response.json())
            raise Exception("Invalid response")
            
        # Throttle to 600 req/15 minutes per API limits
        if self.n_requests == 600 and time.time() - self.start_time <= (60*15):
            print("Sleeping for 15 minutes...")
            time.sleep(60*15)
            self.n_requests = 0
            self.start_time = time.time()

        return response.json()


    def get_activity_details(self, activity_id):
        # We should also get description and device_name from here
        activity_details = self.get_strava(f"activities/{str(activity_id)}")

        # Not all activities have a geometry
        geom = activity_details.get("map", {}).get("polyline", []) or []
        return {
            "description": activity_details.get("description"),
            "device_name": activity_details.get("device_name"),
            "geometry": polyline.decode(geom, geojson=True)
        }


    def get_gear(self, gear_id):
        return self.get_strava(f"gear/{gear_id}")


    def sync_gear(self):
        orphan_gear = self.activity_db.get_orphan_gear()
        if len(orphan_gear) > 0:
            for gear_id in orphan_gear:
                gear_details = self.get_gear(gear_id)
                self.activity_db.insert_gear(gear_details)

            print(f"Added {str(len(orphan_gear))} pieces of gear")
        else:
            print("No new pieces of gear")


    def sync(self, direction = "back"):
        if direction == "back":
            before = self.activity_db.get_oldest_activity()
            time_query = f"before={before}"
        else:
            after = self.activity_db.get_latest_activity()
            time_query = f"after={after}"

        load_more_activies = True
        page = 1

        while load_more_activies:
            activities = self.get_strava(f"athlete/activities?page={page}&per_page={self.page_size}&{time_query}")
            
            if len(activities) < self.page_size:
                load_more_activies = False
            page += 1

            for activity in activities:
                details = self.get_activity_details(activity["id"])
                print(f"{activity['name']}", flush=True)
                self.activity_db.insert_activity({**activity, **details})

        # When done get unique gear_ids and diff with content of gear table
        self.sync_gear()
