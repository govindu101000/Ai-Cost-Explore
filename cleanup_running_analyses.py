import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json

load_dotenv()
url = os.getenv('DATABASE_URL')
if not url:
    raise RuntimeError('DATABASE_URL not set in environment')

with psycopg2.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM analyses WHERE status = 'running';")
        running_before = cur.fetchone()[0]
        print('Running analyses before:', running_before)
        cur.execute(
            "UPDATE analyses SET status = 'failed', analysis_result = %s WHERE status = 'running';",
            (Json({'error': 'cleaned up by admin reset'}),),
        )
        print('Rows updated:', cur.rowcount)
        conn.commit()
        cur.execute("SELECT count(*) FROM analyses WHERE status = 'running';")
        running_after = cur.fetchone()[0]
        print('Running analyses after:', running_after)
