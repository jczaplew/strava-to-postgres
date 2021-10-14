# Strava to Postgres

## Setup

First you will need to create a new Strava application by visiting https://www.strava.com/settings/api

Once you have done that, copy the environment template `cp .env.example .env` and enter your Strava app credentials.

Next, bring the app up using Docker. If it has never been run, it will create the database and import all of your activities. If the database contains exisiting activities, it will attempt to import all new activities.

````bash
docker-compose up
````

## License
MIT