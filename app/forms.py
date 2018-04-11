from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, SelectField, PasswordField
from flask_wtf.html5 import EmailField
from wtforms.validators import DataRequired, Required

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(Form):
	username = StringField("username", validators=[DataRequired()])
	password = PasswordField("password", validators=[DataRequired()])

class SaveForm(Form):
    name = StringField("name", validators=[DataRequired()])

class ImageForm(FlaskForm):
    image = FileField('image', validators=[
    	FileRequired(),
    	FileAllowed(['jpg', 'png'], 'Images only!')
    	])