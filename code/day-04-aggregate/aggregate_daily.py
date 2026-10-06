import psycopg2

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def run_aggregations():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Query to aggregate weather observations grouped by date and coordinates
        aggregation_query = """
            INSERT INTO daily_weather_summary (
                observation_date, latitude, longitude, 
                avg_temp_celsius, min_temp_celsius, max_temp_celsius, 
                avg_windspeed_kmh, dominant_weather_condition, total_records_aggregated
            )
            SELECT 
                DATE(observation_time) AS observation_date,
                latitude,
                longitude,
                ROUND(AVG(temperature_celsius), 2) AS avg_temp_celsius,
                MIN(temperature_celsius) AS min_temp_celsius,
                MAX(temperature_celsius) AS max_temp_celsius,
                ROUND(AVG(windspeed_kmh), 2) AS avg_windspeed_kmh,
                MODE() WITHIN GROUP (ORDER BY weather_condition) AS dominant_weather_condition,
                COUNT(*) AS total_records_aggregated
            FROM analytics_weather
            GROUP BY DATE(observation_time), latitude, longitude
            ON CONFLICT (observation_date, latitude, longitude) 
            DO UPDATE SET
                avg_temp_celsius = EXCLUDED.avg_temp_celsius,
                min_temp_celsius = EXCLUDED.min_temp_celsius,
                max_temp_celsius = EXCLUDED.max_temp_celsius,
                avg_windspeed_kmh = EXCLUDED.avg_windspeed_kmh,
                dominant_weather_condition = EXCLUDED.dominant_weather_condition,
                total_records_aggregated = EXCLUDED.total_records_aggregated,
                created_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(aggregation_query)
        conn.commit()
        
        records_affected = cursor.rowcount
        print(f"✅ Success: Aggregated {records_affected} daily summary record(s) into daily_weather_summary!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Aggregation failed: {e}")

if __name__ == "__main__":
    run_aggregations()