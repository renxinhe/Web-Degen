import sqlite3 as sql
from app import app

#import pix2code classes
from classes.Utils import *
from classes.Compiler import *
from classes.model.pix2code import *
from classes.model.Config import *
from classes.Vocabulary import * 
from classes.Sampler import * 
import sys
import numpy as np

sampler = None
model = None

#load pix2code models only once
# @app.before_first_request
def load_model():
    global sampler, model
    #load pix2code dataset parameters
    meta_dataset = np.load("/home/andrewliu/berkeley/pix2code/bin/meta_dataset.npy")
    input_shape = meta_dataset[0]
    output_size = meta_dataset[1]

    #load pretrained weights
    trained_weights_path = '/home/andrewliu/berkeley/pix2code/bin'
    model = pix2code(input_shape, output_size, trained_weights_path)
    model.load('pix2code')

    #create sampler for generating code
    sampler = Sampler(trained_weights_path, input_shape, output_size, CONTEXT_LENGTH)

def predict(filepath):
    #process image file
    evaluation_img = Utils.get_preprocessed_img(filepath, IMAGE_SIZE)

    #run model prediction using greedy sampler
    result, _  = sampler.predict_greedy(model, np.array([evaluation_img]))

    FILL_WITH_RANDOM_TEXT = True
    TEXT_PLACE_HOLDER = "[]"

    #compile DSL into html
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

    # clean up generated html
    result = result.replace(START_TOKEN, "").replace(END_TOKEN, "")
    return compiler.compile(result.strip(' \t\n\r').split("\n"), rendering_function=render_content_with_text)

# Check if a username/password pair exists in the database
# If so, return that user's ID
def check_up(username, password):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.userid, users.password from users WHERE users.username = ?", (username,)).fetchall()
    if len(result) == 0 or result[0]["password"] != password:
        return False
    else:
        return result[0]["userid"]

# Check if a username does NOT exist in the database, for signup
def check_user(username):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result = cur.execute("select users.username from users WHERE users.username = ?", (username,)).fetchall()
    if len(result) == 0:
        return True
    else:
        return False

# Inserts a new username/password entry into the database, for signup
def sign_up(username, password):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
        userid = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
    return userid

# Retrieves the saved history of a user
def retrieve_saves(user_id):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result =  cur.execute("select entries.id, entries.name, entries.dt from entries WHERE entries.userid = ?", (user_id,)).fetchall()
    return result

# Get the filename for a specific user's saved upload
def get_img(user_id, entryid):
    with sql.connect("app.db") as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        result =  cur.execute("select entries.filename from entries WHERE entries.userid = ? AND entries.id = ?", (str(user_id), entryid)).fetchall()
    return result

# Insert a new entry in a user's history
def save_stuff(userid, name, filename, datetime):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO entries(name, filename, dt, userid) VALUES (?, ?, ?, ?)", (name, filename, datetime, userid))
        userid = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
    return userid

# Delete an entry from a user's history
def delete_save(entryid):
    with sql.connect("app.db") as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("DELETE FROM entries WHERE id = ?", (entryid,))
        conn.commit()
