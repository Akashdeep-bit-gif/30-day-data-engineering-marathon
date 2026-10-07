import psycopg2
import logging
import os

# Configure file logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/data_quality.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def validate_staging_data():
    """Validates records in staging_weather against business quality rules."""
    print("🔍 Starting Data Quality Validation Checks...")
    logging.info("Starting Data Quality Validation Checks...")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Rule 1: Check for Null Values in critical fields
        null_check_query = """
            SELECT id FROM staging_weather 
            WHERE latitude IS NULL OR longitude IS NULL OR temperature IS NULL OR observation_time IS NULL;
        """
        cursor.execute(null_check_query)
        null_records = cursor.fetchall()

        if null_records:
            msg = f"⚠️ QUALITY WARNING: Found {len(null_records)} record(s) with NULL values in critical fields. IDs: {[r[0] for r in null_records]}"
            print(msg)
            logging.warning(msg)
        else:
            msg = "✅ PASS: No critical NULL values found."
            print(msg)
            logging.info(msg)

        # Rule 2: Check for Out-of-Range Temperatures (-50C to +60C)
        temp_range_query = """
            SELECT id, temperature FROM staging_weather 
            WHERE temperature < -50 OR temperature > 60;
        """
        cursor.execute(temp_range_query)
        invalid_temps = cursor.fetchall()

        if invalid_temps:
            msg = f"⚠️ QUALITY WARNING: Found {len(invalid_temps)} record(s) with out-of-range temperatures. IDs: {invalid_temps}"
            print(msg)
            logging.warning(msg)
        else:
            msg = "✅ PASS: All temperatures are within plausible operational bounds (-50°C to +60°C)."
            print(msg)
            logging.info(msg)

        # Rule 3: Check for Invalid Geographical Coordinates
        coord_query = """
            SELECT id, latitude, longitude FROM staging_weather 
            WHERE latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180;
        """
        cursor.execute(coord_query)
        invalid_coords = cursor.fetchall()

        if invalid_coords:
            msg = f"⚠️ QUALITY WARNING: Found {len(invalid_coords)} record(s) with invalid coordinates."
            print(msg)
            logging.warning(msg)
        else:
            msg = "✅ PASS: All geographical coordinates are valid."
            print(msg)
            logging.info(msg)

        # Summary Metrics
        cursor.execute("SELECT COUNT(*) FROM staging_weather;")
        total_staging = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analytics_weather;")
        total_analytics = cursor.fetchone()[0]

        summary_msg = f"📊 DATA AUDIT SUMMARY: Staging Records = {total_staging} | Analytics Records = {total_analytics}"
        print(summary_msg)
        logging.info(summary_msg)

        cursor.close()
        conn.close()

    except Exception as e:
        err_msg = f"❌ Data Quality Check Failed: {e}"
        print(err_msg)
        logging.error(err_msg)

if __name__ == "__main__":
    validate_staging_data()