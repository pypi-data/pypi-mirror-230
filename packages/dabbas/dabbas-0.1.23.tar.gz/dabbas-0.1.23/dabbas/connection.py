import os
from pandas import DataFrame
import urllib.parse
 


def hello():
    print("Hello, World!")


def database_url():
    try:
        pg_url = os.environ['DATABASE_URL']
        return pg_url
    except KeyError:
        pg_user = os.environ.get('PG_USER', 'postgres')
        pg_password = os.environ.get('PG_PASSWORD', 'postgres')
        pg_host = os.environ.get('PG_HOST', 'localhost')
        pg_port = os.environ.get('PG_PORT', 5432)
        pg_dbname = os.environ.get('PG_DBNAME', 'postgres')
        # return f"host='{pg_host}' dbname='{pg_dbname}' user='{pg_user}' password='{pg_password}' port='{pg_port}'"
        return f'postgresql://{pg_user}:{urllib.parse.quote_plus(pg_password)}@{pg_host}:{pg_port}/{pg_dbname}'


def database(url = database_url()):
    from sqlalchemy import create_engine
    return create_engine(url)


def upload(df: DataFrame, name: str, database=database(), **kwargs):
    df.to_sql(name, database, **kwargs)


def connect(url=database_url()):
    import psycopg2
    conn = psycopg2.connect(url)

    return conn


def query(sql, url=database_url()):
    conn = connect(url)
    cur = conn.cursor()

    try:
        # Execute query and fetch results
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        cur.close()
        conn.close()
        raise e
    finally:
        if cur is not None:
            cur.close()
        conn.close()

    return cur.description, results
