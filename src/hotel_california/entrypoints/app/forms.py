from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password')
