from wtforms import Form, StringField, PasswordField, IntegerField, FloatField, DateField, validators, EmailField, BooleanField


class LoginForm(Form):
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password')


def check_positiv_num(form, field):
    if field.data < 0:
        raise validators.ValidationError('Число должно быть больше нуля')


class RoomForm(Form):
    number = IntegerField('Номер', [check_positiv_num])
    capacity = IntegerField('Вместимость', [check_positiv_num])
    price = FloatField('Цена', [check_positiv_num])


def check_departure(form, field):
    if field.data < form.arrival.data:
        raise validators.ValidationError('Дата убытия должна быть раньше чем дата прибытия')


class DatesForm(Form):
    arrival = DateField('Дата прибытия')
    departure = DateField('Дата убытия', [check_departure])


class UserForm(Form):
    name = StringField('User name')
    email = EmailField('Email Address')
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Repeat Password')
    is_admin = BooleanField('Роль админ')
