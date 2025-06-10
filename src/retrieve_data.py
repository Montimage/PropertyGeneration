import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

# Database connection parameters from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def retrieve_examples(description, num_examples=1):
    """
    Retrieves relevant XML property examples from the database based on a textual description.

    If not enough matching examples are found, the function will fetch additional random entries
    from the database to reach the desired number of examples.

    Args:
        description (str): The textual description to search for in the database.
        num_examples (int): The number of examples to retrieve. Default is 1.
    
    Returns:
        List[dict]: A list of dictionaries containing the XML property examples with the following keys:
            - "description": The description of the property.
            - "protocol": A comma-separated string of protocol names.
            - "xml_content": The XML content of the property.
    """

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Retieve the most relevant property based on the description
    cur.execute("""
        SELECT id, name, description, protocol, xml_content, created_at FROM mmt_properties
        WHERE description ILIKE %s
        ORDER BY created_at DESC
        LIMIT %s;
    """, (f"%{description}%", num_examples))


    results = cur.fetchall()
    results_count = len(results)

    # If there are not enough relevant results, fetch random properties to fill the gap
    if results_count < num_examples:
        remaining_needed = num_examples - results_count
        cur.execute("""
            SELECT id, name, description, protocol, xml_content, created_at FROM mmt_properties
            WHERE id NOT IN (
                SELECT id FROM mmt_properties WHERE description ILIKE %s ORDER BY created_at DESC
            )
            ORDER BY RANDOM()
            LIMIT %s;
        """, (f"%{description}%", remaining_needed))

        random_results = cur.fetchall()
        results.extend(random_results)
    
    cur.close()
    conn.close()

    # Format results
    context_data = []
    for row in results:
        context_data.append({
            "description": row[2],
            "protocol": row[3],
            "xml_content": row[4]
        })

    return context_data

def retrieve_protocol_context(protocol_names):
    """
    Retrieves attributes definitions for a given list of protocol names.

    Args:
        protocol_names (List[str]): List of protocol names (e.g., ["ocpp", "mqtt"]).
    
    Returns:
        List[dict]: A list of dictionaries containing the protocol attributes with the following keys:
            - "protocol_name": The name of the protocol.
            - "protocol_attributes": A JSON-formatted list of attributes for the protocol.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    query = """
        SELECT name, attributes FROM protocols
        WHERE name = ANY(%s);
    """

    cur.execute(query, (protocol_names,))
    results = cur.fetchall()

    cur.close()
    conn.close()

    protocol_context = []
    for row in results:
        protocol_context.append({
            "protocol_name": row[0],
            "protocol_attributes": row[1]  # JSON-formatted list of attributes
        })
    return protocol_context