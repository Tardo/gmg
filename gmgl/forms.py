# GMG Copyright 2022 - Alexandre Díaz
from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, Length, url
from wtforms.fields import (
    URLField,
    StringField,
    SubmitField,
    PasswordField,
    HiddenField,
)
from wtforms.widgets import TextArea
from flask_wtf.file import FileField


class LoginForm(FlaskForm):
    username = StringField(lazy_gettext('Username'), validators=[InputRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[InputRequired()])
    submit = SubmitField(lazy_gettext('Submit'))


class UserRegistrationForm(FlaskForm):
    username = StringField(lazy_gettext('Username'), validators=[InputRequired()])
    userpass = PasswordField(
        lazy_gettext('Password'),
        validators=[
            InputRequired(),
            EqualTo('ruserpass', message=lazy_gettext('Passwords must match')),
        ],
    )
    ruserpass = PasswordField(
        lazy_gettext('Repeat Password'), validators=[InputRequired()]
    )
    submit = SubmitField(lazy_gettext('Finish'))


class InstallModForm(FlaskForm):
    file = FileField(lazy_gettext('From File'))
    url = HiddenField(lazy_gettext('From URL'), validators=[url()])


class ResetAdminPasswordForm(FlaskForm):
    skey = StringField(lazy_gettext('Secret Key'), validators=[InputRequired()])
    username = StringField(lazy_gettext('Admin Username'), validators=[InputRequired()])
    userpass = PasswordField(
        lazy_gettext('New Admin Password'),
        validators=[
            InputRequired(),
            EqualTo('ruserpass', message=lazy_gettext('Passwords must match')),
        ],
    )
    ruserpass = PasswordField(
        lazy_gettext('Repeat New Password'), validators=[InputRequired()]
    )
    submit = SubmitField(lazy_gettext('Restore Admin Password'))


class GeneralSearchForm(FlaskForm):
    term = StringField(
        lazy_gettext('Search term'),
        validators=[
            InputRequired(),
            Length(
                min=2, message=lazy_gettext('The length of the search is very small')
            ),
        ],
        render_kw={'placeholder': lazy_gettext('Search usernames, threads, etc...')},
    )


class NLPDemoForm(FlaskForm):
    input_data = StringField(
        lazy_gettext('Input Data'),
        widget=TextArea(),
        validators=[
            InputRequired(),
            Length(max=500, message=lazy_gettext('Maximum length reached!')),
        ],
    )
