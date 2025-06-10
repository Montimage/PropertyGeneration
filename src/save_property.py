import os
import psycopg2
from psycopg2.extras import Json
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def save_property_to_db(description, protocols, name, xml_content):
    """
    Saves a property to the database.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO mmt_properties (description, protocol, name, xml_content)
            VALUES (%s, %s, %s, %s)
        """, (description, protocols, name, xml_content))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False