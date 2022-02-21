from wtforms import Form, StringField, PasswordField, IntegerField, FloatField, validators


class LoginForm(Form):
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password')


def check_positiv_num(form, field):
    if field.data > 0:
        raise validators.ValidationError('Число должно быть больше нуля')


class RoomForm(Form):
    number = IntegerField('Номер', [check_positiv_num])
    capacity = IntegerField('Вместимость', [check_positiv_num])
    price = FloatField('Цена', [check_positiv_num])
