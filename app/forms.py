from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, FloatField, \
    DateField, TimeField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange

from app.models import User, Region, StatusTypes
from datetime import datetime, date, time


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('FirstName', validators=[DataRequired()])
    last_name = StringField('LastName', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class BaseTagsForm(FlaskForm):
    tags = StringField('Tags', validators=[Length(min=0, max=100)])


class BaseNoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=0, max=150)])
    is_private = BooleanField('Public', default=False)
    is_recurring = BooleanField('Recurring', default=False)
    is_shared_with_friends = BooleanField('Share with friends', default=False)
    is_commentable = BooleanField('Comments allowed', default=True)
    # submit = SubmitField('Post note')


class BaseRegionForm(FlaskForm):
    region_name = StringField('Location')
    radius = StringField('Radius', validators=[DataRequired()])
    latitude = StringField('Latitude')
    longitude = StringField('Longitude')

    def validate_region_name(self, region_name):
        if region_name.data:
            region = Region.query.filter_by(name=region_name.data).first()
            if region is None:
                raise ValidationError('The specified region does not exist')


class BaseRecurrenceForm(FlaskForm):
    recurrence_type = SelectField('', choices=[('daily', 'Days'), ('weekly', 'Weeks'),
                                               ('monthly', 'Months'), ('yearly', 'Years'), ('', '')], default='')

    start_time = TimeField('Start Time', validators=[DataRequired()], default=time())

    end_time = TimeField('End Time', validators=[DataRequired()], default=time(23, 59))

    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today)
    end_date = DateField('End Date', validators=[DataRequired()], default=date.today)
    separation_count = IntegerField('', validators=[NumberRange(min=0)], default=0)
    day_of_week = SelectField('', choices=[('7', 'Sundays'), ('1', 'Mondays'), ('2', 'Tuesdays'),
                                           ('3', 'Wednesdays'), ('4', 'Thursdays'), ('5', 'Fridays'),
                                           ('6', 'Saturdays'), ('', '')], default='')
    month_of_year = SelectField('', choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                                             ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                                             ('9', 'September'), ('10', 'October'), ('11', 'November'),
                                             ('12', 'December'), ('', '')], default='')
    # day_of_week = IntegerField('day of the week', validators=[NumberRange(min=1, max=7)])
    week_of_month = IntegerField('week of the month')  # , validators=[NumberRange(min=1, max=5)])
    day_of_month = IntegerField('day of the month')  # , validators=[NumberRange(min=1, max=31)])

    # month_of_year = IntegerField('month of the year', validators=[NumberRange(min=1, max=12)])

    def validate_end_date(self, end_date):
        if self.start_date.data > end_date.data:
            raise ValidationError('End date set before start date')

    def validate_end_time(self, end_time):
        if self.start_time.data > end_time.data:
            raise ValidationError('End time set before start time')


class CreateNoteForm(BaseNoteForm, BaseRecurrenceForm, BaseRegionForm, BaseTagsForm):
    submit = SubmitField('Create Note')


class CreateFilterForm(BaseTagsForm, BaseRegionForm, BaseRecurrenceForm):
    name = StringField('Filter Name', validators=[Length(max=100)])
    status_name = SelectField('', choices=[(str(each_status.id), each_status.name) for each_status in
                                                            StatusTypes.query.order_by('id').all()],
                              default=str(StatusTypes.query.order_by('id').first().id))
    submit = SubmitField('Create Filter')

    def validate_status_name(self, status_name):
        if status_name.data:
            status = StatusTypes.query.get(status_name.data)
            if status is None:
                raise ValidationError('The specified status does not exist')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[Length(min=0, max=150)])
    parent_id = StringField()
    submit = SubmitField('Post comment')


class UserTrackingForm(FlaskForm):
    date = StringField('Date')
    time = StringField('Time')
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    submit = SubmitField('Update User location')


class StatusTypesForm(FlaskForm):
    status_name = SelectField('', choices=[(str(each_status.id), each_status.name) for each_status in
                                           StatusTypes.query.order_by('id').all()],
                              default=str(StatusTypes.query.order_by('id').first().id))
    submit = SubmitField('Change Status')
