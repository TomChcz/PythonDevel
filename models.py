from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime

# create DB variable - new usable instance
db = SQLAlchemy()

# user table structure
class User(db.Model):
	__tablename__ = 'users'
	uid = db.Column(db.Integer, primary_key = True)
	firstname = db.Column(db.String(100))
	lastname = db.Column(db.String(100))
	nickname = db.Column(db.String(100))
	email = db.Column(db.String(120), unique = True)
	pwdhash = db.Column(db.String(54))
	regdate = db.Column(db.DateTime, default=datetime.now)
	grade = db.Column(db.Integer)
	registration_IP = db.Column(db.String(40))
	user_agent = db.Column(db.String(200))
 
	# class constructor
	def __init__(self, firstname, lastname, nickname, email, password, grade, registration_IP, user_agent):
		self.firstname = firstname.title() # first letter capitalized
		self.lastname = lastname.title() # first letter capitalized
		self.nickname = nickname
		self.email = email.lower() # lowercase email to avoid issues
		self.set_password(password) #set_password function defined below
		self.regdate = datetime.now()
		self.grade = grade
		self.registration_IP = registration_IP
		self.user_agent = user_agent

	def set_password(self, password):
		self.pwdhash = generate_password_hash(password) # generate_password_hash from werkzeug

	def check_password(self, password):
		return check_password_hash(self.pwdhash, password) # compares stored (pwdhash) and inputed password


class Test_sizes(db.Model):
	__tablename__ = 'test_sizes'
	uid = db.Column(db.Integer(), primary_key = True)
	test_size = db.Column(db.Integer)

	def __init__(self, test_size):
		self.test_size = test_size

#################### test model for multiple test layouts ###########################


class Dynamic_exercises_structure(db.Model):
	__tablename__ = 'dynamic_exercises_structure'
	uid = db.Column(db.Integer(), primary_key = True)
	grade = db.Column(db.Integer())
	area = db.Column(db.String(100))
	section = db.Column(db.String(200))

	def  __init__(self, grade, area, section):
		self.grade = grade
		self.area = area
		self.section = section



class Dynamic_test(db.Model):
	__tablename__ = 'dynamic_test'
	uid = db.Column(db.Integer(), primary_key = True)
	grade = db.Column(db.Integer())
	area = db.Column(db.String(100))
	section = db.Column(db.String(200))
	template = db.Column(db.String(50)) # tells @app.route('/dynamic_test') which test template will be used to generate HTML + what algorithm to use for evaluation of user answer

	def __init__(self, grade, area, section, template):
		self.grade = grade
		self.area = area
		self.section = section
		self.template = template


class Dynamic_exercises(db.Model):
	__tablename__ = 'dynamic_exercises'
	uid = db.Column(db.Integer(), primary_key = True)
	grade = db.Column(db.Integer()) # trida
	area = db.Column(db.String(100)) # matematika, cz, en
	section = db.Column(db.String(200)) # subkategorie
	description = db.Column(db.String(1000)) # zadani (Najdi ztracene cislo)
	var1 = db.Column(db.String(50)) # prvni cast zadani
	var2 = db.Column(db.String(50)) # druha cast zadani
	solution1 = db.Column(db.String(50))
	solution2 = db.Column(db.String(50))
	points = db.Column(db.Integer())
	language = db.Column(db.String(3))
	template = db.Column(db.String(50)) # tells @app.route('/dynamic_test') which test template will be used to generate HTML + what algorithm to use for evaluation of user answer

	def __init__(self, grade, area, section, description, var1, var2, solution1, solution2, points, language, template):
		self.grade = grade
		self.area = area
		self.section = section
		self.description = description
		self.var1 = var1
		self.var2 = var2
		self.solution1 = solution1
		self.solution2 = solution2
		self.points = points
		self.language = language
		self.template = template


class Test_results(db.Model):
	__tablename__ = 'test_results'
	uid = db.Column(db.Integer(), primary_key = True)
	user_uid = db.Column(db.Integer(), db.ForeignKey('users.uid'))
	grade = db.Column(db.Integer()) # trida
	area = db.Column(db.String(100)) # matematika, cz, en
	section = db.Column(db.String(200)) # subkategorie
	description = db.Column(db.String(1000)) # zadani (Najdi ztracene cislo)
	template = db.Column(db.String(200))
	test_size = db.Column(db.Integer())
	test_type = db.Column(db.String(120)) # regular or repeated test
	score = db.Column(db.Integer())
	points = db.Column(db.Integer())
	date = db.Column(db.DateTime())
	duration_raw = db.Column(db.Numeric())
	week = db.Column(db.Integer())
	user_ip = db.Column(db.String(40))
	user_agent = db.Column(db.String(300))
	duration_formatted = db.Column(db.String(50))
	user_test_order = db.Column(db.Integer())

	def __init__(self, user_uid, grade, area, section, description, template, test_size, test_type, score, points, date, duration_raw, week, user_ip, user_agent, duration_formatted, user_test_order):
		self.user_uid = user_uid
		self.grade = grade
		self.area = area
		self.section = section
		self.description = description
		self.template = template
		self.test_size = test_size
		self.test_type = test_type
		self.score = score
		self.points = points
		self.date = date
		self.duration_raw = duration_raw
		self.week = week
		self.user_ip = user_ip
		self.user_agent = user_agent
		self.duration_formatted = duration_formatted
		self.user_test_order = user_test_order

class Test_results_detail(db.Model):
	__tablename__ = 'test_results_detail'
	uid = db.Column(db.Integer(), primary_key = True)
	test_uid = db.Column(db.Integer(), db.ForeignKey('test_results.uid'))
	user_uid = db.Column(db.Integer(), db.ForeignKey('users.uid'))
	exercise_uid = db.Column(db.Integer(), db.ForeignKey('dynamic_exercises.uid'))
	answer1 = db.Column(db.String(50))
	answer2 = db.Column(db.String(50))
	index = db.Column(db.Integer())
	evaluation = db.Column(db.String(50))
	points = db.Column(db.Integer())
	var1 = db.Column(db.String(50)) # prvni cast zadani
	var2 = db.Column(db.String(50)) # druha cast zadani
	solution1 = db.Column(db.String(50))
	solution2 = db.Column(db.String(50))

	def __init__(self, test_uid, user_uid, exercise_uid, answer1, answer2, index, evaluation, points, var1, var2, solution1, solution2):
		self.test_uid = test_uid
		self.user_uid = user_uid
		self.exercise_uid = exercise_uid
		self.answer1 = answer1
		self.answer2 = answer2
		self.index = index
		self.evaluation = evaluation
		self.points = points
		self.var1 = var1
		self.var2 = var2
		self.solution1 = solution1
		self.solution2 = solution2




'''
class User_ranking(db.Model):
	__tablename__ = 'user_ranking'
	uid = db.Column(db.Integer(), primary_key = True)

	def __init__(self)
'''


## legacy models ##



