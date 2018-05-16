from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupForm(FlaskForm): # defines form fields
	first_name = StringField('Jmeno')
	last_name = StringField('Prijmeni')
	nickname = StringField('Prezdivka', validators=[DataRequired('Prosim vypln svou prezdivku')])
	# email length over certain size (70+ ?) throws unicode error, need to catch that. DB model has 120 chars for email
	email = StringField('Email', validators=[DataRequired('Prosim vypln svuj email'), Email('Prosim vypln email ve spravnem formatu'), Length(max=70, message='Email muze byt maximalne 70 znaku')])
	password = PasswordField('Heslo', validators=[DataRequired('Prosim vypln svoje heslo'), Length(min=6, message='Heslo musi byt delsi nez 5 znaku')])
	grade = IntegerField('Tvoje trida', validators=[NumberRange(min=1, max=9, message='1 to 9'), DataRequired('Prosim vypln tridu 1 az 9')])
	submit = SubmitField('Zaregistrovat') 

class LoginForm(FlaskForm):
	email = StringField('Email', validators =[DataRequired('Prosim vypln svuj email'), Email('Prosim vypln email ve spravnem formatu')])
	password = PasswordField('Heslo', validators=[DataRequired('Prosim vypln svoje heslo')])
	submit = SubmitField('Prihlasit se')

class TestSelectorForm(FlaskForm):
	# change all to select field
	grade = IntegerField('Rocnik') # trida na ZS 
	area = SelectField('Predmet') # matematika, cestina a ostatni (TBD)
	topic = SelectField('Oblast') # Prirozena cisla, Ciselna osa, atd