from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class RegisterForm(FlaskForm):
    """Form for creating new users."""

    username = StringField('Username', validators=[DataRequired()])

    password = StringField('Password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Form for creating new users."""

    username = StringField('Username', validators=[DataRequired()])

    password = StringField('Password', validators=[DataRequired()])

    