from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    user_name = StringField('user name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    is_remember = BooleanField('is remember')
    submit = SubmitField('登录')


class SignupForm(Form):
    user_name = StringField('user name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('注册')