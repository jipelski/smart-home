from dotenv import load_dotenv
import psycopg2
import os
from datetime import datetime, timedelta

load_dotenv()

DATABASE_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

def update_daily_aggregates():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT type, structure FROM abstract_sensors")
    abstract_sensors = cursor.fetchall()

    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)


    for sensor_type, structure in abstract_sensors:
        features = structure.keys()

        aggregation_query = f"SELECT sensor_id"

        for feature in features:
            aggregation_query += f", AVG({feature}) AS avg_{feature}, MIN({feature}) AS min_{feature}, MAX({feature}) AS max_{feature}"

        aggregation_query += f" FROM {sensor_type} WHERE timestamp::date = %s" 

        cursor.execute(aggregation_query, (previous_date,))
        results = cursor.fetchall()

        for result in results:
            sensor_id = result[0]
            insert_query = f"""
                INSERT INTO {sensor_type}_aggregates (sensor_id, date
            """
            for feature in features:
                insert_query += f", avg_{feature}, min_{feature}, max_{feature}"

            insert_query += ") VALUES (%s, %s"
            insert_query += ", ".join(["%s", "%s", "%s"] * len(features))
            insert_query += ")"

            
            values = [sensor_id, previous_date]
            for i in range(1, len(result)):
                values.append(result[i])

            cursor.execute(insert_query, tuple(values))
    
    conn.commit()
    cursor.close()
    conn.close()
