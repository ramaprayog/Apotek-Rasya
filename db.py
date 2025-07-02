import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="db_fix",
        user="postgres",
        password="Aisyahprayoga8624",
        host="localhost",
        port="5432"
    )