from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, BooleanField


class RegisterForm(FlaskForm):
    email = StringField()
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    DOB = StringField()
    postcode = StringField()
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField()
    password = PasswordField()
    pin = StringField()
    recaptcha = RecaptchaField()
    postcode = StringField()
    login = SubmitField()


class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField()
    newpassword = PasswordField()
    confirmpassword = PasswordField()
    submit = SubmitField()