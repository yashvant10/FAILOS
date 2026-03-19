import psycopg2
import sys

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Yash12211@1",
        host="db.nbsehwzthsezdswyttzq.supabase.co",
        port="5432",
        connect_timeout=10
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
