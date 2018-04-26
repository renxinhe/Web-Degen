import sqlite3 as sql
from app import app


from classes.Utils import *
from classes.Compiler import *
from classes.model.Config import *
from classes.Vocabulary import * 
sampler = None
model = None
@app.before_first_request
def load_model():

    import sys
    import numpy as np
    from os.path import basename
    from classes.Sampler import Sampler
    from classes.model.pix2code import pix2code
    from classes.model.Config import CONTEXT_LENGTH
    print('loading')
    global sampler, model
    meta_dataset = np.load("/home/andrewliu/berkeley/pix2code/bin/meta_dataset.npy")
    input_shape = meta_dataset[0]
    output_size = meta_dataset[1]

    trained_weights_path = '/home/andrewliu/berkeley/pix2code/bin'
    model = pix2code(input_shape, output_size, trained_weights_path)
    model.load('pix2code')

    sampler = Sampler(trained_weights_path, input_shape, output_size, CONTEXT_LENGTH)

def predict(filepath):
    from classes.Utils import Utils
    import numpy as np
    evaluation_img = Utils.get_preprocessed_img(filepath, IMAGE_SIZE)

    beam_width = 1
    print("Search with beam width: {}".format(beam_width))
    result, _ = sampler.predict_beam_search(model, np.array([evaluation_img]), beam_width=beam_width)
    print("Result beam: {}".format(result))

    import sys

    from os.path import basename

    FILL_WITH_RANDOM_TEXT = True
    TEXT_PLACE_HOLDER = "[]"

    dsl_path = "assets/web-dsl-mapping.json"
    compiler = Compiler(dsl_path)

    def render_content_with_text(key, value):
        if FILL_WITH_RANDOM_TEXT:
            if key.find("btn") != -1:
                value = value.replace(TEXT_PLACE_HOLDER, Utils.get_random_text())
            elif key.find("title") != -1:
                value = value.replace(TEXT_PLACE_HOLDER, Utils.get_random_text(length_text=5, space_number=0))
            elif key.find("text") != -1:
                value = value.replace(TEXT_PLACE_HOLDER,
                                      Utils.get_random_text(length_text=56, space_number=7, with_upper_case=False))
        return value
    result = result.replace(START_TOKEN, "").replace(END_TOKEN, "")
    print(result.strip(' \t\n\r').split("\n"))
    return compiler.compile(result.strip(' \t\n\r').split("\n"), rendering_function=render_content_with_text)


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
        result =  cur.execute("select entries.id, entries.name, entries.dt from entries WHERE entries.userid = " + str(user_id)).fetchall()
    return result

def get_img(user_id, entryid):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result =  cur.execute("select entries.filename from entries WHERE entries.userid = ?", str(user_id)).fetchall()
    return result

# TODO
def save_stuff(userid, name, filename, datetime, data):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO entries(name, filename, dt, userid) VALUES (?, ?, ?, ?)", (name, filename, datetime, userid))
        userid = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
    return userid

def delete_save(entryid):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("DELETE FROM entries WHERE id =" + str(entryid))
        conn.commit()
