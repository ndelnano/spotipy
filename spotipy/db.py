from dotenv import load_dotenv
import MySQLdb

# Ensure secrets are loaded
load_dotenv()

HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PWD = os.getenv('DB_PASS')
DB = os.getenv('DB_NAME')

def conn():
    return MySQLdb.connect(host=HOST, user=USER, passwd=PWD, db=DB)

def get_tokens_for_user(username):
    conn = conn()
    cur = MySQLdb.cursors.DictCursor(conn)
    cur.execute("""
        SELECT 
            spotify_auth_token, 
            spotify_refresh_token, 
            expires_at
        FROM user 
            WHERE username = %s
        """, (username))
    return cur.fetchone()

def update_token_for_user(username, token_info):
    conn = conn()
    cur = MySQLdb.cursors.DictCursor(conn)
    return cur.execute("""
        UPDATE users
        SET 
            spotify_auth_token = %s,
            expires_at = %s
        WHERE username = %s
        """, (token_info['access_token'], token_info['expires_at'], username))

