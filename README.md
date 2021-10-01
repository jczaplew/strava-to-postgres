# Strava to Postgres

## Setup

A few dependencies are required:
````
poetry
postgresql
````

1. `cp .env.example .env`
2. Enter your database and Strava app credentials in `.env`
3. Install the Python dependencies with `poetry install`
4. Create the database - `createdb activities && psql -d activities < schema.sql`

## Usage



## License
MIT