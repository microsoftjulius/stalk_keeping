from flask_wtf import FlaskForm
from wtforms import StringField, FileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf.file import FileAllowed


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=150)])
    submit = SubmitField('Save')
