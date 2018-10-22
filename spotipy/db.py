import os
import sys

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
    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute("""
        SELECT 
            spotify_auth_token, 
            spotify_refresh_token, 
            expires_at
        FROM users
            WHERE username =%s
        """, (username,))
    result = cur.fetchone()
    if not result:
        print('did not find user in db, exiting')
        sys.exit(1)
    else:
        user = dict()
        user['refresh_token'] = result['spotify_refresh_token']
        user['access_token'] = result['spotify_auth_token']
        user['expires_at'] = result['expires_at']
        return user

def update_token_for_user(username, token_info):
    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute("""
        UPDATE users
        SET 
            spotify_auth_token = %s,
            expires_at = %s
        WHERE username = %s
        """, (token_info['access_token'], str(token_info['expires_at']), username,))
    con.commit()
