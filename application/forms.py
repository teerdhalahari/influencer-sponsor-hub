from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from application.model import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdRequestForm(FlaskForm):
    influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
    messages = TextAreaField('Messages')
    requirements = TextAreaField('Requirements')
    payment_amount = DecimalField('Payment Amount', places=2)
    submit = SubmitField('Submit')

    


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    platform = RadioField('Platform', choices=[('youtube', 'YouTube'), ('instagram', 'Instagram'), ('twitter', 'Twitter')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class CampaignForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    status_choices = [('Active', 'Active'), ('Inactive', 'Inactive')]
    status = SelectField('Status', choices=status_choices, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    budget = DecimalField('Budget', validators=[DataRequired()])

    def validate_end_date(self, field):
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')

    submit = SubmitField('Create Campaign')


