import psycopg2
import sys
try:
    conn = psycopg2.connect('postgresql://brvm_user:brvm_password@127.0.0.1:5432/brvm_tracker')
    print('OK - psycopg2 connected successfully!')
    conn.close()
except Exception as e:
    print('ERROR psycopg2:', repr(e))
    sys.exit(1)
