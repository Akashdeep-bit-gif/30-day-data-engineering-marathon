import psycopg2
import time

DB_CONFIG = {
    "dbname": "data_engineering_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432"
}

def benchmark_queries():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    start = time.time()
    cursor.execute("EXPLAIN ANALYZE SELECT * FROM analytics_weather WHERE observation_time >= NOW() - INTERVAL '7 days';")
    plan = cursor.fetchall()
    duration = round((time.time() - start) * 1000, 2)
    
    print(f"⚡ Query Benchmark Execution Time: {duration} ms")
    for line in plan:
        print(f"  {line[0]}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    benchmark_queries()
