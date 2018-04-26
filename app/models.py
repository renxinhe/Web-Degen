import sqlite3 as sql

def retrieve_users():
    # SQL statement to query database goes here
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.userid, users.username from users").fetchall()
    return result

def retrieve_username():
    # SQL statement to query database goes here
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.username from users").fetchall()
    return result

##You might have additional functions to access the database
def check_up(username, password):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.userid, users.password from users WHERE users.username ='" + username + "'").fetchall()
    if len(result) == 0 or result[0]["password"] != password:
        return False
    else:
        return result[0]["userid"]

def check_user(username):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.username from users WHERE users.username ='" + username + "'").fetchall()
    if len(result) == 0:
        return True
    else:
        return False
    
def sign_up(username, password):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
        userid = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
    return userid

# TODO
def retrieve_saves(user_id):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select 1").fetchall()
    return result

# TODO
def save_stuff(name, filename, data):
    print('Saving %s...' % name)
    return