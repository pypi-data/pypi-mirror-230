import json
import jsonschema
import psycopg2
from psycopg2.extras import RealDictCursor
import os


# Get the directory of the current Python file
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the JSON file
schema_file_path = os.path.join(current_directory, 'schema.json')

with open(schema_file_path) as f:
    schema = json.load(f)

def validate_json(json_data):
    try:
        jsonschema.validate(json_data, schema)
        print("JSON rules are valid")
    except Exception as e:
        raise ("JSON rules are not valid:", e)


def load_rules_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            validate_json(json_data)
            return json_data
    except Exception as e:
        raise Exception(f"Invalid JSON file or schema mismatch , error: {e}")

def load_rules_from_json(json_data):
    try:
        validate_json(json_data)
        return json_data
    except Exception as e:
        raise Exception(f"Invalid JSON file or schema mismatch , error: {e}")
    
def load_rules_from_postgres(settings):
    try:
        conn = psycopg2.connect(
            host=settings.host,
            database=settings.database,
            user=settings.user,
            password=settings.password,
            port=settings.port
        )

        # Create a cursor object
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Execute SQL query to fetch JSON data
        query = "SELECT rules FROM routing_rules;"
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()
        # rules = json.dumps(rows[0])
        row = rows[0]
        rules = row.get('rules')
        # Close the cursor and connection
        cursor.close()
        conn.close()
        # print(f'rules {rules}')
    except Exception as e:
        raise Exception(f'error fetching rules from database: {e} ')
    try:
        validate_json(rules)
        return rules
    except Exception as e:
        raise Exception(f"Invalid JSON file or schema mismatch , error: {e}")