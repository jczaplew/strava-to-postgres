# Strava to Postgres
Sync your Strava data to a Postgres database using the Strava API. If you've ever found yourself asking questions that Strava is unable to answer ("How many hours have I ridden my mountain bike since May?", "How does my average speed vary based on which bike I'm riding?", etc) but has the data for, this is for you.

This can also serve as a foundation for any sort of app you might want to build on top of this data.

## Setup

First you will need to create a new Strava application by visiting https://www.strava.com/settings/api

Once you have done that, copy the environment template `cp .env.example .env` and enter your Strava app credentials.

Next, bring the app up using Docker. If it has never been run, you will be prompted to log in to your Strava account and authorize the application you created. It will also create the database and import all of your activities. If the database contains exisiting activities, it will attempt to import all new activities.

````bash
docker-compose up
````

## Visualize
Included is a QGIS layout `activities.qgz` that can be used to visualize your data on a map

## License
MIT