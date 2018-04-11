import os

from flask import render_template, redirect, request, session
from app import app, models, db
from .forms import *
# Access the models file to use SQL functions
from .models import *

from werkzeug.utils import secure_filename

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        users = retrieve_username()
        user_id = check_up(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect('/upload')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

# TODO: make login and signup one page with two buttons
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        users = check_user(username);
        if not users:
            return render_template('signup.html', form=form)
        else:
            user_id = sign_up(username, password)
            session['user_id'] = user_id
            return redirect('/upload')
        
    return render_template('signup.html', form=form)

# https://flask-wtf.readthedocs.io/en/stable/form.html#module-flask_wtf.file
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # Retreive trips for this user from DB
    form = ImageForm()
    if "user_id" in session:
        user_id = session["user_id"]
        if form.validate_on_submit():
            f = form.image.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.instance_path, 'photos', filename))
            session["filename"] = filename
            return redirect("/preview")

        saves = retrieve_saves(user_id)
        return render_template('upload.html', form=form, saves=saves)
    return redirect("/login")

@app.route('/preview', methods=['POST', 'GET'])
def preview():
    # import pdb; pdb.set_trace()
    form = SaveForm()
    filename = session["filename"]
    data = get_preview()

    if form.validate_on_submit():
        name = form.name.data
        save_stuff(name, filename, data)
        return redirect('/upload')
    if request.method == 'POST' and request.form['submit'] == 'Discard':
        return redirect('/upload')

    return render_template('preview.html', form=form, preview=data)

# TODO: get HTML preview or whatever is generated from image
def get_preview():
    return

@app.route('/delete/<value>', methods=['GET', 'POST'])
def delete(value):
    delete_save(value)
    return redirect('/upload')

@app.route('/download/<value>', methods=['GET', 'POST'])
def download(value):
    download_save(value)
    return redirect('/upload')
