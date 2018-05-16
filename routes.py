from flask import Flask, render_template, request, session, redirect, url_for, flash, abort
from models import db, User, Test_results, Test_results_detail, Test_sizes, Dynamic_test, Dynamic_exercises, Dynamic_exercises_structure
from forms import SignupForm, LoginForm, TestSelectorForm
from collections import OrderedDict # sorts the dictionary
# from sqlalchemy.sql.expression import func # selects random rows
from datetime import datetime, timedelta
from time import time
from helpers import convert_duration
from sqlalchemy import and_
from config import grades
from sqlalchemy import distinct, func

app = Flask(__name__)

# connect to DB

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/learningflask'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qukkwepweeojql:cd59e06a0fe91e241d721be370572e697b27a25d388bab7294d1e66f910d54eb@ec2-184-73-199-72.compute-1.amazonaws.com:5432/d1kufo1vr7gadl'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # supress flask's warning

db.init_app(app)

app.secret_key ='development-key' # CSRF protecion. not needed if ' form.csrf_token ' is used in form


@app.route('/')
def index():

	# preload exercise structure, return separately math, czech and english datasets
	
	math_exercises_structure = Dynamic_exercises_structure.query.filter_by(area='math').all()
	test_sizes = Test_sizes.query.all()
	
	# load form
	# temporarily disabled form = TestSelectorForm()

	math_tests = Dynamic_exercises_structure.query.filter_by(area='math').all()


	return render_template('index.html', math_exercises_structure=math_exercises_structure, math_tests=math_tests, grades=grades, test_sizes=test_sizes)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	
	# check if user already logged in and redirect home
	if 'email' in session:
		return redirect(url_for('dashboard'))

	form = SignupForm() # new usable instance of signupform

	# if request coming from form
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signup.html', form=form)
		else:
			# check if user with submitted email exists
			email = form.email.data
			user = User.query.filter_by(email=email).first()
			
			# render error with custom message if email already taken
			if user is not None:
				emailerr = "Email already used"
				return render_template('signup.html', emailerr=emailerr, form=form)

			# check whether nickname exists
			nickname = form.nickname.data
			user1 = User.query.filter_by(nickname=nickname).first()

			if user1 is not None:
				nickerr = "Prezdivka uz je pouzita"
				return render_template('signup.html', nickerr=nickerr, form=form)

			# create new instance of User object and add to db

			registration_IP = request.environ['REMOTE_ADDR']
			user_agent = request.headers.get('User-Agent')
			newuser = User(form.first_name.data, form.last_name.data, form.nickname.data, form.email.data, form.password.data, form.grade.data, registration_IP, user_agent)
			db.session.add(newuser)
			db.session.commit()
			
			# remember user
			session['email'] = newuser.email # any field can be used 
			return redirect(url_for('dashboard'))
	
	# if adress requested directly (aka www.something/signup), render form
	elif request.method == 'GET':
		return render_template('signup.html', form=form)


@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():

	# check if user logged in
	if 'email' not in session:
		form = LoginForm()
		# custom message for users trying to access homepage without being logged in
		homeaccess_err = "Prosím nejdříve se přihlaš"
		return render_template('login.html', form=form, homeaccess_err=homeaccess_err)
	else:

		# load user
		user = User.query.filter_by(email=session.get('email')).first()

		# load tests

		test_sizes = Test_sizes.query.all()
		math_tests = Dynamic_exercises_structure.query.filter_by(area='math').all()

		return render_template('dashboard.html', user=user, test_sizes=test_sizes, math_tests=math_tests, grades=grades)


# logs the user in
@app.route('/login', methods=['GET', 'POST'])
def login():
	
	# check if user already logged in and redirect home
	if 'email' in session:
		return redirect(url_for('dashboard'))

	form = LoginForm()
	
	if request.method == 'POST':
		# validate form, render login page agan if fields empty
		if form.validate() == False:
			return render_template('login.html', form=form)
		else:
			# get submitted data
			email = form.email.data
			password = form.password.data

			# query db for user data .first returns first row
			user = User.query.filter_by(email=email).first()
			
			# user exists and password confirms
			if user is not None and user.check_password(password):
				
				# remember user
				session['email'] = form.email.data
				return redirect(url_for('dashboard'))
			
			# user exists, password does not confirm
			elif user is not None and user.check_password(password) == False:
				errmsg = 'Wrong password or login'
				return render_template('login.html', form=form, errmsg=errmsg)
			
			# user does not exist
			else:
				errmsg = 'Wrong login or password'
				return render_template('login.html', form=form, errmsg=errmsg)
	
	elif request.method == 'GET':
		return render_template('login.html', form=form)



@app.route('/dynamic_test', methods = ['GET', 'POST'])
def dynamic_test():
	
	if request.method == 'POST':

		test_type = request.form.get('test_type')

		if test_type != 'Normální': # if repeated test
			
			if test_type == 'Opakovaný':
				test_results_detail = Test_results_detail.query.filter_by(test_uid=int(request.form.get('test_uid'))).with_entities(Test_results_detail.exercise_uid).order_by(Test_results_detail.index).all()

			elif test_type == 'Opakovaný - původní s chybou':
				test_results_detail = Test_results_detail.query.filter_by(test_uid=int(request.form.get('test_uid'))).filter_by(evaluation='Špatně').with_entities(Test_results_detail.exercise_uid).order_by(Test_results_detail.index).all()
			'''
			exercise_uids = []

			for i in test_results_detail:
				exercise_uids.append(i.exercise_uid)
			'''

			test = []

			for i in test_results_detail:
				data = Dynamic_exercises.query.filter_by(uid=i.exercise_uid).first()
				test.append(data)

			test_start = time()

			msg = None

			return render_template('dynamic_test.html', test=test, test_start=test_start, msg=msg, test_size=len(test), test_type=test_type)

		elif test_type == 'Normální':
			
			test_size = int(request.form.get('test_size'))
			
			# pick a section
			section = Dynamic_exercises.query.filter_by(area='math', section=request.form.get('section')).order_by(func.random()).first()
			# then select description
			description = Dynamic_exercises.query.filter_by(description=section.description).order_by(func.random()).first()
			# then select random exercise // looks like duplicity - can be deleted	
			test = Dynamic_exercises.query.filter_by(description=description.description).order_by(func.random()).limit(test_size).all()

			test_start = time()

			if len(test) < test_size:
				msg = 1
			else:
				msg = None

			# note that test type is specified here directly - need to check this for repeated tests
			return render_template('dynamic_test.html', test=test, test_start=test_start, msg=msg, test_size=test_size, test_type=test_type)
	
	elif request.method == 'GET':
		return redirect(url_for('dashboard'))


@app.route('/dynamic_test_eval', methods=['GET', 'POST'])
def dynamic_test_eval():

	# check if user logged in
	if 'email' in session:
		user_uid = User.query.filter_by(email=session.get('email')).first().uid
	else:
		user_uid = 9 # temp ID for non registered users

	# get test parameters
	test_size = int(request.form.get('test_size'))
	template = request.form.get('template')
	grade = int(request.form.get('grade'))
	area = request.form.get('area')
	section = request.form.get('section')
	description = request.form.get('description')
	test_type = request.form.get('test_type')

	# duration
	test_start = request.form.get('test_start')
	test_end = time()

	duration_raw = float(float(test_end) - float(test_start))
	week = datetime.now().isocalendar()[1]

	# user data
	user_ip = request.environ['REMOTE_ADDR']
	user_agent = request.headers.get('User-Agent')

	# load test data & answers

	exercise_uids = request.form.getlist('exercise_uid')

	variables1 = request.form.getlist('variable1')
	variables2 = request.form.getlist('variable2')
	
	answers1 = request.form.getlist('answer1')
	answers2 = request.form.getlist('answer2')

	solutions1 = request.form.getlist('solution1')
	solutions2 = request.form.getlist('solution2')

	points_list = request.form.getlist('points')
	
	# evaluates(sorts) exercises, where sorting of random order digits is needed and solution is not provided from db of exercises
	if solutions1[0] == 'sortascend': # need to change this to simpler variable
		solutions1 = sorted(variables1, key=int)
	elif solutions1[0] == 'sortdescend':
		solutions1 = sorted(variables1, key=int, reverse=True)

	
	# calculate user score based on template. sol2 (exerise has 2 component solution) = 2 solutions needed

	evaluation = []
	points_detail = []
	points_total = 0

	correct = 0

	if 'sol2' in template:
		for i in range(test_size):
			if (answers1[i] == solutions1[i] and answers2[i] == solutions2[i]):
				evaluation.append('Správně')
				correct += 1
				points_total += int(points_list[i])
				points_detail.append(int(points_list[i]))
			else:
				evaluation.append('Špatně')
				points_detail.append(0)
	else: # only 1 solution for the exercise
		for i in range(test_size):
			if answers1[i] == solutions1[i]:
				evaluation.append('Správně')
				correct += 1
				points_total += int(points_list[i])
				points_detail.append(int(points_list[i]))
			else:
				evaluation.append('Špatně')
				points_detail.append(0)
			# answers2.append('na') # add 'na' value so the answers2[] list is created with na values and exists, otherwise throws error

	score = int((correct / test_size) * 100)

	# convert secs into list with dd hh mm ss

	duration_formatted = convert_duration(duration_raw)


	###### save test into DB

	# get current user tests

	previous_user_tests = db.session.query(Test_results).filter(Test_results.user_uid == user_uid).order_by(Test_results.uid.desc()).first()



	# check for errors (nonetype return value)


	if not previous_user_tests or not previous_user_tests.user_test_order:
		user_test_order = 1
	else:
		user_test_order = (previous_user_tests.user_test_order + 1)

	new_test_result = Test_results(user_uid, grade, area, section, description, template, test_size, test_type, score, points_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), duration_raw, week, user_ip, user_agent, duration_formatted, user_test_order)

	db.session.add(new_test_result)
	db.session.commit()

	test_uids = Test_results.query.filter_by(user_uid=user_uid).all() # can probably go away

	# get uid of latest user test_results record (the one currently saved to DB) - used to add to detailed test results for each user
	obj = db.session.query(Test_results).filter(Test_results.user_uid == user_uid).order_by(Test_results.uid.desc()).first()
	test_uid = obj.uid

	# test_uid = test_uids[-1].uid # gets last test_uid



	# return str(test_uid) + str(user_uid) + ' ' + str(obj.uid)

	# save detailed test data
	for i in range(test_size):
		new_test_results_detail = Test_results_detail(test_uid, user_uid, exercise_uids[i], answers1[i], answers2[i], i, evaluation[i], points_detail[i], variables1[i], variables2[i], solutions1[i], solutions2[i])
		db.session.add(new_test_results_detail)

	db.session.commit()

	# load test results from db for display on results page
	test_results = Test_results.query.filter_by(uid=test_uid).first()
	test_results_detail = Test_results_detail.query.filter_by(test_uid=test_uid).order_by(Test_results_detail.index).all()


	return render_template('dynamic_test_result.html', test_results=test_results, test_results_detail=test_results_detail, test_type=test_type)


# shows historical tests

@app.route('/test_archive')
def test_archive():

	if 'email' not in session:
		form = LoginForm()
		# custom message for users trying to access homepage without being logged in
		homeaccess_err = "Prosím nejdřív se přihlaš"
		return render_template('login.html', form=form, homeaccess_err=homeaccess_err)
	else:
		
		user = User.query.filter_by(email=session.get('email')).first()
		test_results = Test_results.query.filter_by(user_uid=user.uid).order_by(Test_results.date).all()


		# load tests

		test_sizes = Test_sizes.query.all()
		math_tests = Dynamic_exercises_structure.query.filter_by(area='math').all()

		return render_template('test_archive_list.html', user=user, test_results=test_results, grades=grades, test_sizes=test_sizes, math_tests=math_tests)


@app.route('/tests/')
@app.route('/tests/<test_uid>')
def tests(test_uid=None):
	
	# redirect for tests/ without test_id
	if 'email' not in session:
		form = LoginForm()
		# custom message for users trying to access homepage without being logged in
		homeaccess_err = "Prosím nejdříve se přihlaš"
		return render_template('login.html', form=form, homeaccess_err=homeaccess_err)
	elif not test_uid:
		flash('Nebylo zadáno ID testu')
		return redirect(url_for('test_archive'))

	else:
		user = User.query.filter_by(email=session.get('email')).first()
		# the following 2 queries have to be joined
		test_results = Test_results.query.filter_by(uid=test_uid).first()
		test_results_detail = Test_results_detail.query.filter_by(test_uid=test_uid).order_by(Test_results_detail.index).all()
		
		

		# check if test exists
		if not test_results or not test_results_detail:
			flash('Test neexistuje')
			return redirect(url_for('test_archive'))
		else:
			# check if user allowed to view content
			if user.uid == test_results.user_uid:

				# get list of all user tests, get unique id for each user from DB
				user_tests = Test_results.query.filter_by(user_uid=user.uid).order_by(Test_results.user_test_order).all()

				# current test order id
				current_test = test_results.user_test_order
				total_tests_taken = len(user_tests)

				prev_test = 0
				next_test = 0

				if total_tests_taken  == 1:
					prev_test = None
					next_test = None
				if total_tests_taken > 1:
					if current_test == 1:
						prev_test = None
					else:
						prev_test = user_tests[current_test - 2].uid
					if current_test == total_tests_taken:
						next_test == None
					else:
						next_test = user_tests[current_test].uid

					 # does not add +1 since list of user_tests has is zero indexed




		

				return render_template('test_archive.html', prev_test=prev_test, next_test=next_test, test_results=test_results, test_results_detail=test_results_detail, user_tests=user_tests, current_test=current_test, total_tests_taken=total_tests_taken)
			else:
				flash('K tomuto testu nemáš přístup (není tvůj)')
				return redirect(url_for('test_archive'))

# logs the user our
@app.route('/logout')
def logout():

	# delete cookie
	session.pop('email', None)
	return redirect(url_for('index'))

@app.route('/sysinfo')
def sysinfo():

	# get system info
	sections = db.session.query(Dynamic_exercises_structure).count()
	descriptions = db.session.query(Dynamic_exercises).distinct(Dynamic_exercises.description).count()
	exercises = db.session.query(Dynamic_exercises).distinct(Dynamic_exercises.uid).count()
	users = db.session.query(User).count()
	tests = db.session.query(Test_results).count()
	tests_exercises = db.session.query(Test_results_detail).count()
	tests_success = db.session.query(Test_results).filter(Test_results.score == 100).count()
	tests_exercises_success = db.session.query(Test_results_detail).filter(Test_results_detail.evaluation == 'Správně').count()

	if tests:
		tests_success_rate = (tests_success / tests) * 100
		exercises_success_rate = (tests_exercises_success / tests_exercises) * 100
	else:
		tests_success_rate = 'ještě nejsou žádné testy'
		exercises_success_rate = 'ještě nejsou žádné testy'


	return render_template('sysinfo.html', sections=sections, descriptions=descriptions, exercises=exercises, users=users, tests=tests, 
		tests_exercises=tests_exercises, tests_success=tests_success, tests_exercises_success=tests_exercises_success, 
		tests_success_rate=tests_success_rate, exercises_success_rate=exercises_success_rate)

# runs the app in debug
if __name__ == '__main__':
	app.run(debug=True) # !!! DONT RUN IN DEBUG ON PUBLIC - security risk !!!