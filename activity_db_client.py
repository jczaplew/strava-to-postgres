import psycopg
from psycopg.types.json import Jsonb
from os import environ
from dotenv import load_dotenv

load_dotenv()

class ActivityDBClient:
    def __init__(self):
        dbname = environ.get("DB_NAME", "activities")
        db_user = environ.get("DB_USER")
        db_password = environ.get("DB_PASSWORD")
        db_port = environ.get("DB_PORT", "5432")
        db_host = environ.get("DB_HOST", "localhost")
        self.connection = psycopg.connect(f"dbname={dbname} host={db_host} user={db_user} password={db_password} port={db_port}")
        self.cursor = self.connection.cursor()


    def insert_activity(self, activity):
        # TODO: Ensure we don't insert duplicates

        # Insert into db
        print(f"{activity['name']}", flush=True)
        try:
            self.cursor.execute(""" 
                INSERT INTO activities (source, source_id, name, description, activity, start_time, moving_time, elapsed_time, distance, elevation_gain, average_speed, max_speed, gear_id, trainer, commute, other, geom)
                VALUES ('strava', %(id)s, %(name)s, %(description)s, %(activity)s, %(start_time)s, %(moving_time)s, %(elapsed_time)s, %(distance)s, %(elevation_gain)s, %(average_speed)s, %(max_speed)s, %(gear_id)s, %(trainer)s, %(commute)s, %(other)s, ST_GeomFromGeoJSON(%(geometry)s))
            """, {
                "id": activity["id"],
                "name": activity["name"],
                "description": activity["description"],
                "activity": activity["type"],
                "start_time": activity["start_date_local"],
                "moving_time": activity.get("moving_time", 0),
                "elapsed_time": activity.get("elapsed_time", 0),
                # Convert metric to customary
                "distance": round(activity.get("distance", 0) * 0.000621371, 2),
                "elevation_gain":round(activity.get("total_elevation_gain", 0) * 3.28084, 2),
                "average_speed": round(activity.get("average_speed", 0) * 2.23694,  2),
                "max_speed": round(activity.get("max_speed", 0) * 2.23694, 2),
                "gear_id": activity.get("gear_id"),
                "trainer": activity["trainer"],
                "commute": activity["commute"],
                "other": Jsonb({
                    "average_watts": activity.get("average_watts", 0),
                    "external_id": activity.get("external_id"),
                    "upload_id": activity["upload_id"],
                    "device_name": activity["device_name"]
                }),
                "geometry": Jsonb({"type": "LineString", "coordinates": activity["geometry"]})
            })
            self.connection.commit()

        except Exception as e:
            print(activity)
            raise e


    def get_orphan_gear(self):
        self.cursor.execute("""
            SELECT DISTINCT gear_id FROM activities WHERE gear_id NOT IN (SELECT DISTINCT source_id FROM gear)
        """)
        return [row[0] for row in self.cursor.fetchall()]


    def insert_gear(self, gear_activity):
        self.cursor.execute(""" 
            INSERT INTO gear (source, source_id, name, brand, model, description)
            VALUES ('strava', %(source_id)s, %(name)s, %(brand)s, %(model)s, %(description)s)
        """, {
            "source_id": gear_activity.get("id"),
            "name": gear_activity.get("name"),
            "brand": gear_activity.get("brand_name"),
            "model": gear_activity.get("model_name"),
            "description": gear_activity.get("description")
        })
        self.connection.commit()
    

    def get_oldest_activity(self):
        self.cursor.execute("select start_time from activities order by start_time asc limit 1")
        result = self.cursor.fetchall()
        return result[0][0].timestamp() if len(result) == 1 else "" 


    def get_latest_activity(self):
        self.cursor.execute("select start_time from activities order by start_time desc limit 1")
        result = self.cursor.fetchall()
        return result[0][0].timestamp() if len(result) == 1 else "" 
    