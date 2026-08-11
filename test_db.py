import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('DATABASE_URL')
print(f"Testing connection to: {url}")

try:
    conn = psycopg2.connect(url, sslmode='require')
    print("? Database connected successfully!")
    conn.close()
except Exception as e:
    print(f"? Connection failed: {e}")
