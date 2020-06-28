from flask import Flask, jsonify, request, json
from flask_mysqldb import MySQL
import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask import jsonify, make_response
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("C://Users//Eliza//Desktop//catalog-fii-server-master//server.crt", "C://Users//Eliza//Desktop//catalog-fii-server-master//server.key")

app = Flask(__name__)
@app.route('/')
def index():
	return 'Hello world'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'licenta'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'secret'
mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)
@app.route('/users/logout', methods=['POST'])
def logout():
	email = request.get_json()['email']
	token = request.get_json()['token']
	print(email)
	print(token)
	cur = mysql.connection.cursor()
	cur.execute("DELETE from auth where token=token")
	mysql.connection.commit()
	result = {
		"email": email,
		"token": token
 	}
	return jsonify({'result': result})

@app.route('/users/register', methods=['POST'])
def register():
	cur = mysql.connection.cursor()
	first_name = request.get_json()['first_name']
	last_name = request.get_json()['last_name']
	email = request.get_json()['email']
	password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
	registration_number = request.get_json()['registration_number']
	group = request.get_json()['group']
	year = request.get_json()['year']
	cur.execute(
		"INSERT INTO students (first_name, last_name,registration_number, `year`, `group`,email,password) VALUES ('" +
		str(first_name) + "', '" +
		str(last_name) + "', '" +
		str(registration_number) + "', '" +
		str(year) + "', '" +
		str(group) + "', '" +
		str(email) + "', '" +
		str(password) +"')")
	mysql.connection.commit()
	result = {
		'first_name': first_name,
		'last_name': last_name,
		'email': email,
		'password': password,
		'registration_number': registration_number,
		'group': group,
		'year': year
	}

	return jsonify({'result': result})

from datetime import date
@app.route('/users/login', methods=['POST'])
def login():
	cur = mysql.connection.cursor()
	email = request.get_json()['email']
	password = request.get_json()['password']
	type = request.get_json()['type']
	if(str(type)=="students"):
		cur.execute("SELECT * FROM students where email = '" + str(email) + "'")
		rv = cur.fetchone()
		if bcrypt.check_password_hash(rv['password'], password):
			access_token = create_access_token(
				identity={'first_name':rv['first_name'],'last_name':rv['last_name'],'email': rv['email'],'registration_number':rv['registration_number'],
						  'group':rv['group'],'year':rv['year']})
			result = jsonify({"token": access_token})
			cur.execute("SELECT id_student FROM students where email = '" + str(email) + "'")
			rv = cur.fetchone()
			id_student = rv.get('id_student')
			cur.execute(
				"INSERT INTO auth (id_user,token, user_type,`date`) VALUES ('" +
				str(id_student) + "', '" +
				str(access_token) + "', '" +
				str(type) + "', '" +
				str(date.today()) + "')")
			mysql.connection.commit()
		else:
			result = jsonify({"error": "Invalid username and password"})
		return result

	else:
		cur.execute("SELECT * FROM professors where email = '" + str(email) + "'")
		rv = cur.fetchone()
		if bcrypt.check_password_hash(rv['password'], password):
			access_token = create_access_token(
				identity={'first_name': rv['first_name'], 'last_name': rv['last_name'], 'email': rv['email']})

			result = jsonify({"token": access_token})

			cur.execute("SELECT id_prof FROM professors where email = '" + str(email) + "'")
			rv = cur.fetchone()
			id_prof = rv.get('id_prof')
			cur.execute(
				"INSERT INTO auth (id_user,token, user_type,`date`) VALUES ('" +
				str(id_prof) + "', '" +
				str(access_token) + "', '" +
				str(type) + "', '" +
				str(date.today()) + "')")
			mysql.connection.commit()
		else:
			result = jsonify({"error": "Invalid username and password"})


		return result




from random import randint
@app.route('/users/present', methods=['POST','GET'])
def generate_code():
	cur = mysql.connection.cursor()
	type = request.get_json()['type']
	if (str(type) == "students"):
		codStud = request.get_json()['codIntrodus']
		studentEmail = request.get_json(['studentEmail'])
		email_student=studentEmail.get("studentEmail")
		cur.execute("SELECT * FROM codes where code = '" + str(codStud) + "'")
		rows = cur.fetchone()
		#print(rows)
		if (rows == None):
			print("nu exista codul")
			# result = jsonify({"cod_prezenta": "aici iti pun un mesaj daca nu e bun codu"})
			result = jsonify({"mesaj": "Codul introdus nu este corect "})
			return result
		else:
			print("exista codul")
			cur.execute("SELECT id_student FROM students WHERE email LIKE %s", [email_student])
			rv = cur.fetchall()
			l = []
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					id_student = i[j]
			#print(id_student)
			cur.execute("SELECT id_prof FROM codes where code = '" + str(codStud) + "'")
			rv = cur.fetchall()
			l = []
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					id_prof = i[j]
			cur.execute("SELECT subject FROM codes where code = '" + str(codStud) + "'")
			rv = cur.fetchall()
			l = []
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					subject = i[j]
			cur.execute("SELECT class_number FROM codes where code = '" + str(codStud) + "'")
			rv = cur.fetchall()
			l = []
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					class_number = i[j]
			cur.execute(
				"INSERT INTO presents (id_student, id_prof,subject, `date`, class_number) VALUES ('" +
				str(id_student) + "', '" +
				str(id_prof) + "', '" +
				str(subject) + "', '" +
				str(date.today()) + "', '" +
				str(class_number) + "')")
			mysql.connection.commit()#try daca se poate, se afiseaza mesajul de mai jos, daca nu se afiseaza "cod incorect"
			result = jsonify({"mesaj": "Prezenta adaugata cu succes la materia " + str(subject) +" in data de " + str(date.today())})
			return result
	if(str(type)=="professors"):
		print(request.get_json())
		profEmail = request.get_json()['email']
		cur = mysql.connection.cursor()
		cur.execute(
			"SELECT distinct subjects.subject_name from subjects join didactic on didactic.id_subject=subjects.id_subject join professors on professors.id_prof=didactic.id_prof where professors.email='" + str(profEmail) + "'")
		rows = cur.fetchall()
		print(rows)
		print({"subject_name": list(rows)})
		result = jsonify({"subject_name": list(rows)})
		return result

@app.route('/users/nou', methods=['POST'])
def k():
	cur = mysql.connection.cursor()
	email_prof = request.get_json()['email']
	cur.execute( "SELECT id_prof FROM professors WHERE email LIKE %s", [email_prof] )
	rv = cur.fetchall()
	l=[]
	for i in rv:
		l.append(i)
	for i in l:
		for j in i:
			id_prof = i[j]
	print(id_prof)
	materie = request.get_json()['materie']
	print(materie)
	tipOra = request.get_json()['tipOra']
	print(type(tipOra))
	concatenate_subject=""
	concatenate_subject+=materie
	concatenate_subject+=" "
	concatenate_subject+=tipOra
	print(concatenate_subject)
	nrOra = request.get_json()['nrOra']
	print(str(nrOra))
	range_start = 10 ** (6 - 1)
	range_end = (10 ** 6) - 1
	code = randint(range_start, range_end)
	cur.execute(
		"INSERT INTO codes (code,id_prof, class_number,subject) VALUES ('" +
		str(code) + "', '" +
		str(id_prof) + "', '" +
		str(nrOra) + "', '" +
		str(concatenate_subject) + "')")
	mysql.connection.commit()
	result = jsonify({"cod_prezenta": code})
	return result

@app.route('/users/subjects/prefessors', methods=['POST'])
def addGrades():
	email = request.get_json()['email'] #preiau mailul profului, si trimit matriile la care preda
	#print(str(email))
	cur = mysql.connection.cursor()
	cur.execute(
		"SELECT distinct subjects.subject_name from subjects join didactic on didactic.id_subject=subjects.id_subject join professors on professors.id_prof=didactic.id_prof where professors.email='" + str(
			email) + "'")
	rows = cur.fetchall()
	#print("rows",rows)
	#print({"subject_name": list(rows)})
	result = jsonify({"subject_name": list(rows)})
	return result

@app.route('/users/subjects/prefessors2', methods=['POST'])
def addGrades2():
	email = request.get_json()['email']
	subject=request.get_json()['subject']
	print("aici")
	print(str(subject))
	print(str(email))
	cur = mysql.connection.cursor()#de preluat grupele la care preda la materia respectiva
	cur.execute("SELECT id_prof FROM professors where email = %s", [email])
	rv = cur.fetchone()
	id_prof = rv.get('id_prof')
	cur.execute("SELECT id_subject FROM subjects where subject_name = %s", [subject])
	rv = cur.fetchone()
	id_subject = rv.get('id_subject')
	cur.execute(
		"SELECT distinct didactic.group from didactic where id_prof=%s and id_subject=%s", [id_prof, id_subject])
	rows = cur.fetchall()
	#print("rows",rows)
	#print({"grupe": list(rows)})
	result = jsonify({"list_group": list(rows)})
	return result

@app.route('/users/subjects/prefessors3', methods=['POST'])
def addGrades3():
	email = request.get_json()['email']
	subject=request.get_json()['subject']
	grupa=request.get_json()['g']
	gradeType=request.get_json()['gradeType']
	an=0
	if str(gradeType)=="Laborator" or str(gradeType)=="Test Laborator" or str(gradeType)=="Tema":
		numbr=request.get_json()['numbr']
		print(str(numbr))
	cur = mysql.connection.cursor()
	cur.execute("SELECT `year` from subjects where subject_name=%s", [subject])
	rv1 = cur.fetchall()
	for i in rv1:
		an=i.get("year")
	cur = mysql.connection.cursor()
	cur.execute("SELECT first_name,last_name from students where `group`=%s and `year`=%s order by first_name, last_name",[grupa,an])  # studentii din anul in care se preda materia respectiva
	rv = cur.fetchall()
	result = jsonify({"response": rv})
	return result

@app.route('/users/subjects/students', methods=['POST'])
def showGrades1():
	email = request.get_json()['email']
	cur = mysql.connection.cursor()
	cur.execute("SELECT year from students where email LIKE %s", [email])
	rvv = cur.fetchall()
	for i in rvv:
		for j in i:
			year = i[j]
	today = datetime.datetime.today()
	luna = today.month
	ziua = today.day
	if (luna == 2 and ziua >= 14):
		semestru = 2
	else:
		if (luna > 2 and luna < 8):
			semestru = 2
		else:
			semestru = 1
	#cur.execute
	cur.execute("SELECT subject_name from subjects where year LIKE %s", [year])
	rv = cur.fetchall()
	result = jsonify({"subject_name": list(rv)})
	return result

@app.route('/users/subjects/students2', methods=['POST'])
def showGrades2():
	email = request.get_json()['email']
	subject = request.get_json()['subject']
	cur = mysql.connection.cursor()
	# de afisat notele la subjectul de sus ale studentului cu mailul de sus
	cur.execute("SELECT exam, partial,laboratory_score,laboratory_test,homework,project from grades join subjects on grades.id_subject=subjects.id_subject join students on students.id_student=grades.id_student where subjects.subject_name LIKE %s and email LIKE %s",[subject,email]);
	rv=cur.fetchall()
	l_exam=[]
	l_partial=[]
	l_homework=[]
	l_laboratory_score=[]
	l_laboratory_test=[]
	l_project=[]
	for i in rv:
		for j in i:
			if i[j]:
				if "exam" in j:
					l_exam.append(i[j])
				else:
					if "laboratory_score" in j:
						l_laboratory_score.append(i[j])
					else:
						if "laboratory_test" in j:
							l_laboratory_test.append(i[j])
						else:
							if "homework" in j:
								l_homework.append(i[j])
							else:
								if "partial" in j:
									l_partial.append(i[j])
								else:
									if "project" in j:
										l_project.append(i[j])

	#return l_exam,l_partial,l_homework,l_laboratory_score,l_laboratory_test
	#rows = cur.fetchall()
	# print(rows)
	# print({"subject_name": list(rows)})
	cur = mysql.connection.cursor()
	cur.execute("SELECT id_student from students where email=%s", [email])
	rv2 = cur.fetchall()
	for i in rv2:
		id_student = i.get("id_student")
	cur.execute("SELECT date, subject,class_number from presents where id_student=%s and subject LIKE %s",
				[id_student, "%" + subject + "%"])
	rv1 = cur.fetchall()
	l = []
	for i in rv1:
		prezenta = ""
		data = i.get("date")
		materie = i.get("subject")
		class_num = i.get("class_number")
		prezenta += "Prezenta la clasa " + str(class_num) + " pe data de: "+str(data) + " la materia: "
		prezenta += str(materie)
		l.append(prezenta)
	cur.execute("SELECT finalgrade from finalgrades where id_student=%s and subject LIKE %s",
				[id_student, "%" + subject + "%"])
	nota_finala=cur.fetchall()
#print("Nota Finala", nota_finala[0]['finalgrade'])
	result = jsonify({"grade": rv,"present":l,"finalgrade": nota_finala[0]['finalgrade']})
	return result



@app.route('/users/titular', methods=['POST'])
def titular():
	email = request.get_json()['email']
	cur = mysql.connection.cursor()
	cur.execute("SELECT distinct didactic.title from didactic join professors on didactic.id_prof=professors.id_prof where professors.email=%s",[email])
	rv = cur.fetchall()
	for i in rv:
		if "titular" == i.get("title"):
			result = jsonify({"titular": 'da'})
			return result
	result = jsonify({"titular": 'nu'})
	return result


@app.route('/users/formula', methods=['POST'])
def formula():
	email = request.get_json()['email']
	print(str(email))
	cur = mysql.connection.cursor()
	cur.execute("SELECT distinct subjects.subject_name from subjects join didactic on didactic.id_subject=subjects.id_subject join professors on professors.id_prof=didactic.id_prof where professors.email=%s and didactic.title='titular'",[email] )
	rv = cur.fetchall()
	result = jsonify({"subject_name": rv})
	return result



import re
import string
@app.route('/users/formula2', methods=['POST'])
def formula2():
	tip_funct = ["count", "avg", "sum"]
	email = request.get_json()['email']
	materia = request.get_json()['materia']
	alese = request.get_json()['alese']
	cate = request.get_json()['cate']
	conditii = request.get_json()['conditii']
	formula = request.get_json()['formula']
	aprox = request.get_json()['aprox']
	print("DETALII FORMULA")
	print("email:",email)
	print("materia:", materia)
	print("alese:", alese)#tip note
	print("cate:", cate)
	print("conditii:", conditii)
	print("formula:", formula)
	print("aprox:", aprox)
	print(type(aprox))
	T = cate.get("T")
	H = cate.get("H")
	A = cate.get("A")
	print("NOUL ALESE",alese)
	for i in range(1, int(T)+1):
		a = "T" + str(i)
		alese.append(a)
	for j in range(1, int(A) + 1):
		b = "A" + str(j)
		alese.append(b)



	def is_correct(formula,alese):
		count = 0
		for i in range(0, len(formula)):
			if formula[i] == "(":
				count += 1
			elif formula[i] == ")":
				count -= 1
			if count < 0:
				return False
		lista_litere = []
		res = re.findall(r'\w+', formula)
		for i in res:
			if i.isnumeric() == False:
				lista_litere.append(i)
		#print("Notatiile din formula:", lista_litere)
		for i in lista_litere:
			if i not in alese and i not in tip_funct:
				print(i)
				return "Nu ati respectat notatiile"


		semne = ["+", "-", "^", "%", "*", "/"]
		litere_mici = list(string.ascii_lowercase)
		litere_mari = list(string.ascii_uppercase)
		litere = litere_mari + litere_mici

		for i in range(1, len(formula)):
			if formula[i] in semne and (formula[i + 1] not in litere and formula[i + 1] != "(" and formula[i + 1].isnumeric() == False):
				return "if 1"
			if formula[i] in semne and (formula[i - 1] not in litere and formula[i - 1] != ")" and formula[i - 1].isnumeric() == False):
				print(formula[i])
				print(i)
				return "if 2"
		return "Expresie scrisa corect"




	def separe(F, T, A, T_score, A_score):
		for i in range(1, int(T) + 1):
			a = "T" + str(i)
			if a in F:
				x = F.replace(a, str(T_score[str(i)]))
				F = x
		for j in range(1, int(A) + 1):
			b = "A" + str(j)
			if b in F:
				y = F.replace(b, str(A_score[str(j)]))
				F = y
		return F
	def cnt(F,id_student,materia):
		l = F.split("count")
		print("Split dupa count:", l)
		i = []
		for s in l:
			q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa count
			i.append(q)  # pun in lista primele paranteze de dupa fiecare count
		print("Lista cu primele paranteze de dupa fiecare count:", i)

		lista_rezultate = []
		print("caut pentru studentul", id_student)
		for j in i:
			if (j):
				if ("P" == j):
					caut= materia+" Laborator/Seminar"
					cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",[id_student,caut])
					rv = cur.fetchall()
					print("p lab",rv)
					for kk in rv:
						for j in kk:
							count_present = kk[j]
					print("numarul prezentelor la  Laborator/Seminar este: ", count_present)
					lista_rezultate.append(count_present)

				if ("PC" == j):
					caut = materia + " Curs"
					cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",[id_student,caut])
					rv = cur.fetchall()
					print("p curs",rv)
					for kk in rv:
						for j in kk:
							count_present = kk[j]
					print("numarul prezentelor la Curs este: ", count_present)
					lista_rezultate.append(count_present)

				if ("PCons" == j):
					caut = materia + " Consultatie"
					cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",[id_student,caut])
					rv = cur.fetchall()
					for kk in rv:
						for j in kk:
							count_present = kk[j]
					print("numarul prezentelor la Consultatii este: ", count_present)
					lista_rezultate.append(count_present)

		print("Lista rezultate expresii cu count:", lista_rezultate)
		print("F initial:", F)

		#daca lista e goala, sa o umplem cu 0
		#print(i)
		#x = F.replace("count("+ i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
		#print("Replace doar la prima paranteza:", x)
		del(i[0])
		#print(i)
		for m in range(0, len(lista_rezultate)):
			for k in range(m, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
				print("Parantezele pe care le caut:", "count(" + i[k] + ")")
				F = F.replace("count(" + i[k] + ")",str(lista_rezultate[m]))
				break # inlocuiesc counturile urile pe care le gasesc
		print("Replace la tot: ", F)
		return F



	def avg(F,scoreT,scoreH,scoreA,E):
		cur = mysql.connection.cursor()
		cur.execute("SELECT prop from subjects where subject_name=%s", [materia])
		rv = cur.fetchall()
		for i in rv:
			x = i.get("prop")
		prop1 = re.findall(r'\b\d+\b', x)
		T = prop1[0]
		H = prop1[1]
		A = prop1[2]
		l = F.split("avg")
		print("Split dupa avg:", l)
		i = []
		for s in l:  # parcurg lista cu splitul dupa avg
			q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa avg
			i.append(q)  # pun in lista primele paranteze de dupa fiecare avg
		print("Lista cu primele paranteze de dupa fiecare avg:", i)
		lista_rezultate = []
		for j in i:
			if (j):
				if ("A" in j): #de preluat din bd jsonul de A
					suma = sum(scoreA.values())
					nr_laboratoare = int(A)
					media_laborator = suma / float(nr_laboratoare)
					lista_rezultate.append(media_laborator)
				else:
					if ("H" in j):#de preluat din bd jsonul de H
						suma = sum(scoreH.values())
						nr_teme = int(H)
						media_laborator = suma / float(nr_teme)
						lista_rezultate.append(media_laborator)
					else:
						if ("T" in j):#de preluat din bd jsonul de T
							suma = sum(scoreT.values())
							print("BAAFSFSDFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:",suma)
							nr_tl = int(T)
							print(nr_tl)
							media_laborator = suma / float(nr_tl)
							print(media_laborator)
							lista_rezultate.append(media_laborator)
						else:
							count_plusuri = j.count("+")
							count_plusuri += 1
							lista_rezultate.append((eval(j) / float(count_plusuri)))
		print("Lista rezultate expresii cu avg:", lista_rezultate)
		print("F initial:", F)

		x = F.replace("avg(" + i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
		print("Replace doar la prima paranteza:", x)

		for m in range(1, len(lista_rezultate)):
			for k in range(1, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
				print("Parantezele pe care le caut:", "avg(" + i[k] + ")")
				x = x.replace("avg(" + i[k] + ")", str(lista_rezultate[m]))  # inlocuiesc avg urile pe care le gasesc

			print("Replace la tot: ", x)
		# print("Nota: ",eval(x))
		return x

	def suma(F,scoreT,scoreH,scoreA):
		l = F.split("sum")
		print("Split dupa sum:", l)
		i = []
		for s in l:  # parcurg lista cu splitul dupa avg
			q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa avg
			i.append(q)  # pun in lista primele paranteze de dupa fiecare avg
		print("Lista cu primele paranteze de dupa fiecare sum:", i)
		lista_rezultate = []
		for j in i:
			if (j):
				if ("A" in j):
					lista_rezultate.append(sum(scoreA.values()))#de preluat din bd jsonul de A
				else:
					if ("H" in j):
						lista_rezultate.append(sum(scoreH.values()))#de preluat din bd jsonul de H
					else:
						if ("T" in j):
							lista_rezultate.append(sum(scoreT.values()))#de preluat din bd jsonul de T

		print("Lista rezultate expresii cu sum:", lista_rezultate)
		print("F initial:", F)
		x = F.replace("sum(" + i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
		print("Replace doar la prima paranteza:", x)
		for m in range(1, len(lista_rezultate)):
			for k in range(1, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
				print("Parantezele pe care le caut:", "sum(" + i[k] + ")")
				x = x.replace("sum(" + i[k] + ")", str(lista_rezultate[m]))  # inlocuiesc avg urile pe care le gasesc

			print("Replace la tot: ", x)
		return x

	import math
	def final_grade(N, aprox_fgrade,materia,cati_studenti):
		if N <= 4.5:
			return 4
		grades = []
		if (aprox_fgrade == "Aproximare prin adaos"):
			if (N - math.floor(N) >= 0.5):
				return math.ceil(N)
			else:
				return math.floor(N)
		else:
			if (aprox_fgrade == "Aproximare prin trunchiere"):
				return math.floor(N)
			else:
				if (aprox_fgrade == "Gauss"):
					cur = mysql.connection.cursor()
					cur.execute("SELECT grade from finalgrades where subject=%s order by grade desc",[materia])
					rv = cur.fetchall()
					lista_note_studenti = []
					for i in rv:
						lista_note_studenti.append(float(i.get("grade")))
					s = cati_studenti
					grade10= s * 0.05
					grade9 = s * 0.1
					grade8 = s * 0.2
					grade7 = s * 0.3
					grade6 = s * 0.2
					grade5 = s * 0.1
					grades.append(math.ceil(grade10))
					grades.append(math.ceil(grade9))
					grades.append(math.ceil(grade8))
					grades.append(math.ceil(grade7))
					grades.append(math.ceil(grade6))
					grades.append(math.ceil(grade5))
					print("Cati o sa aiba 10 9 ..",grades)
					nota_actuala=10
					noua_lista=[]
					print("NOTE BD",lista_note_studenti)
					for i in grades:
						for ceva in range (0,i):
							noua_lista.append(nota_actuala)
						nota_actuala=nota_actuala-1
					print("noua listaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",noua_lista)
					pos=0
					for i in range(0, len(lista_note_studenti)):
						if lista_note_studenti[i] == round(N,1):
							pos = i
							print("Pozitia notei in lista descrescatoare: ", pos)
							break
					print(pos)
					return noua_lista[pos]


	print("Corectitudine: ",is_correct(formula,alese))
	if(is_correct(formula,alese)=="Expresie scrisa corect"):
		k = len(conditii)
		for i in conditii:
			if(is_correct(i.get('conditie'),alese)!="Expresie scrisa corect"):
				k = k-1
				result = jsonify({"response": "Exista o conditie scrisa gresit"})
				return result
			if (is_correct(i.get('conditie'), alese) == "Nu ati respectat notatiile"):
				k = k - 1
				result = jsonify({"response": "Nu ati respectat notatiile"})
				return result
			'''
			if "PCons" in i.get('conditie') and "count(PCons)" not in i.get('conditie'):
				result = jsonify({"response": "Exista o conditie scrisa gresit PCons"})
				return result

			if "PC" in i.get('conditie') and "count(PC)" not in i.get('conditie'):
				result = jsonify({"response": "Exista o conditie scrisa gresit PC"})
				return result
			
			if "P" in i.get('conditie') and "count(P)" not in i.get('conditie'):
				result = jsonify({"response": "Exista o conditie scrisa gresit P"})
				return result
			'''

		if (k==len(conditii)):
			cur = mysql.connection.cursor()
			cur.execute(
				"UPDATE subjects SET formula = %s  where subject_name LIKE %s", [formula, materia])
			cur.execute("UPDATE subjects SET prop=%s where subject_name=%s",[cate,materia])
			mysql.connection.commit()
			cur = mysql.connection.cursor()
			cur.execute("SELECT prop from subjects where subject_name=%s", [materia])
			rv = cur.fetchall()
			for i in rv:
				x = i.get("prop")
			prop1 = re.findall(r'\b\d+\b', x)
			T = prop1[0]
			H = prop1[1]
			A = prop1[2]
			cur = mysql.connection.cursor()
			cur.execute("SELECT id_subject from subjects where subject_name=%s", [materia])
			rv = cur.fetchall()
			l = []
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					id_subject = i[j]
			#print(id_subject)
			cur.execute("SELECT `year` from subjects where id_subject=%s",[id_subject])
			rvvv=cur.fetchall()
			for i in rvvv:
				l.append(i)
			for i in l:
				for j in i:
					an = i[j]
			cur = mysql.connection.cursor()
			cur.execute("SELECT id_student from students where `year`=%s",[an])
			result = cur.fetchall()
			students = []
			for i in result:
				for j in i:
					students.append(i[j])
			print("dadaaaaaaaaaaaaaaaaa",students) #iduri studenti sunt stocate ca si o lista
			#print(type(students))
			cati_studenti=len(students)
			for i in students:
				E = 0
				print("STUDENTUL: ",i)
				if "E" in formula:
					cur.execute("SELECT exam from grades where id_student=%s and id_subject=%s",[i, id_subject])
					rv = cur.fetchall()
					if not rv:
						E = 0
					else:
						for ip in rv:
							if ip!=None:
								E = ip.get("exam")
					#print("E",E)
				if "PR" in formula:
					cur.execute("SELECT partial from grades where id_student=%s and id_subject=%s", [i, id_subject])
					rv = cur.fetchall()
					if not rv:
						PR = 0
					else:
						for ip in rv:
							if ip!= None:
								PR = ip.get("partial")
					#print("PR", PR)

				if "PJ" in formula:
					cur.execute("SELECT project from grades where id_student=%s and id_subject=%s", [i, id_subject])
					rv = cur.fetchall()
					if not rv:
						PJ = 0
					else:
						for ip in rv:
							if ip != None:
								PJ = ip.get("project")
					#print("PJ", PJ)

				cur.execute("SELECT laboratory_score from grades where id_student=%s and id_subject=%s",[i,id_subject])
				rv = cur.fetchall()
				if len(rv)==0:
					scoreA = {}
					for k in range(1, int(T) + 1):
						scoreA[str(k)] = 0
				else:
					for j in rv:
						A_score = j.get("laboratory_score")
						if (A_score != None):
							scoreA = json.loads(A_score)
						else:
							scoreA = {}
							for k in range(1, int(A) + 1):
								scoreA[str(k)] = 0
				#print("scoreA",scoreA)

				cur.execute("SELECT laboratory_test from grades where id_student=%s and id_subject=%s",[i,id_subject])
				rv = cur.fetchall()
				if len(rv)==0:
					scoreT = {}
					for k in range(1, int(T) + 1):
						scoreT[str(k)] = 0
				else:
					for j in rv:
						T_score = j.get("laboratory_test")
						print("TTTTTTTTTTTTT",T_score)
						if (T_score != None):
							scoreT = json.loads(T_score)
						else:
								scoreT = {}
								for k in range(1, int(T) + 1):
									scoreT[str(k)] = 0
				print("scoreT", scoreT)

				cur.execute("SELECT homework from grades where id_student=%s and id_subject=%s", [i, id_subject])
				rv = cur.fetchall()
				if len(rv)==0:
					scoreH = {}
					for k in range(1, int(T) + 1):
						scoreH[str(k)] = 0
				else:
					for j in rv:
						H_score = j.get("homework")
						if (H_score != None):
							scoreH = json.loads(H_score)
						else:
							scoreH = {}
							for k in range(1, int(H) + 1):
								scoreH[str(k)] = 0
				#print("scoreH", scoreH)

				#print("Formula dupa separe pentru stud",i," :",separe(formula,T,A,scoreT,scoreA))

				F = separe(formula,T,A,scoreT,scoreA)
				print(F)
				if "count" in F:
					z = cnt(F,i,materia)
					F = z

				if "avg" in F:
					x = avg(F,scoreT,scoreH,scoreA,E)
					print("x actual: ", x)
					F = x
					if "sum" in x:
						y = suma(x,scoreT,scoreH,scoreA)
						print("y actual: ", y)
						F = y
				else:
					if "avg" not in F and "sum" in F:
						y = suma(F,scoreT,scoreH,scoreA)
						F = y

				print("formula inainte de eval:",F)

				N = eval(str(F))
				trecut = 1
				cond = ""
				print("Nota finala",N)

				for condition in conditii:
					e = separe(condition.get('conditie'),T,A,scoreT,scoreA)
					if "PR" in e:
						cur.execute("SELECT partial from grades where id_student=%s and id_subject=%s", [i, id_subject])
						rv = cur.fetchall()
						if not rv:
							PR = 0
						else:
							for ip in rv:
								if ip != None:
									PR = ip.get("partial")
					# print("PR", PR)
					print("EEEEEEEEE",e)
					if "P" in e and "count" not in e:
						result = jsonify({"response": "Eroare la conditii"})
						return result

					if "count" in e:
						e = cnt(e, i, materia)

					if "avg" in e:
						x = avg(e, scoreT, scoreH, scoreA,E)
						print("x actual: ", x)
						e = x
						if "sum" in x:
							y = suma(x, scoreT, scoreH, scoreA)
							print("y actual: ", y)
							print(eval(str(y)))
							e = y
					else:
						if "avg" not in e and "sum" in e:
							y = suma(e, scoreT, scoreH, scoreA)
							e = y
					if (eval(e) == False):
						trecut = 0
						cond = condition
						break
				if (trecut == 0):
					print("Elevul nu a promovat materia pentru ca nu a respectat conditia: ", cond)


				print("Nota: ", N)#de bagat N in bd la grade studnetul i la materia =[materia]
				mysql.connection.cursor()

				print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",N, i ,materia)
				cur.execute("SELECT grade from finalgrades where id_student=%s and subject=%s",[i,materia])
				rv = cur.fetchall()
				l = []
				g = ""
				for ii in rv:
					l.append(ii)
				for ii in l:
					for j in ii:
						g = ii[j]
				print(rv)
				print("GGGGGGGGGG",g)
				print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",type(N))
				print(N,i,materia)
				cur.execute("SELECT * from finalgrades where id_student=%s and subject=%s",[i,materia])
				rv100=cur.fetchall()
				print("MAMAAAA",rv)
				if (rv100):
					cur.execute("UPDATE finalgrades set grade=%s WHERE id_student=%s and subject=%s", [N, i, materia])
					mysql.connection.commit()
				else:
					cur.execute(
						"INSERT INTO finalgrades (id_student,subject,grade) VALUES ('" +
						str(i) + "', '" +
						str(materia) + "', '" +
						str(N) + "')")
					mysql.connection.commit()



				print("1-trecut, 0-altfel : ", trecut)
				NFinal=final_grade(N, aprox,materia,cati_studenti)
				mysql.connection.cursor()
				print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK", NFinal, i, materia)
				cur.execute("UPDATE finalgrades set finalgrade=%s WHERE id_student=%s and subject=%s",[NFinal, i, materia])
				mysql.connection.commit()
				if (trecut == 0):
					print("Elevul nu a promovat materia pentru ca nu a respectat conditia: ", cond)
					picat = 4
					cur.execute("UPDATE finalgrades set finalgrade=%s WHERE id_student=%s and subject=%s",[picat, i, materia])
					mysql.connection.commit()
		#print(conditii)
		result = jsonify({"response": is_correct(formula, alese)})
		return result


@app.route('/users/notele', methods=['GET','POST'])
def noteStudenti():
	materia = request.get_json()['subject']
	grupa = request.get_json()['g']
	tip_note = request.get_json()['gradeType']
	try:
		nr_lab = request.get_json()['numbr']
	except:
		nr_lab = None
	note = request.get_json()['paramsArray']
	print("Materia: ", str(materia))
	print("Grupa: ", str(grupa))
	print("type grupa",type(grupa))
	print("Tip nota: ", str(tip_note))
	print("Nr. nota: ", str(nr_lab))
	print("Note: ", str(note))
	cur = mysql.connection.cursor()
	# AFISARE TOTI STUDENTII DINTR O ANUMITA GRUPA
	cur.execute("SELECT `year` from subjects where subject_name=%s", [materia])
	rv1 = cur.fetchall()
	for i in rv1:
		an = i.get("year")
	cur.execute("SELECT id_student from students where `group`=%s and `year`=%s order by first_name,last_name", [grupa, an])
	result = cur.fetchall()
	students = []
	for i in result:
		for j in i:
			students.append(i[j])
	# ID UL MATERIEI LA CARE PROFUL VREA SA PUNA NOTA
	cur.execute("SELECT id_subject from subjects where subject_name=%s",[materia])
	rv = cur.fetchall()
	l = []
	for i in rv:
		l.append(i)
	for i in l:
		for j in i:
			id_subject = i[j]
	print("ID_MATERIE",id_subject)
	nr_nota = 0
	if str(tip_note) == "Laborator":
		for id_s in students:
			print("ID STUDENT", id_s)
			# sql = "SELECT homework from grades where id_student=%s and id_subject=%s"
			# data_tuple = (id_s, id_subject)
			# cur.execute(sql, data_tuple)
			cur.execute("SELECT * from grades where id_student=%s and id_subject=%s", [id_s, id_subject])
			rv = cur.fetchall()
			l = []
			lab_s = ""
			for i in rv:
				l.append(i)
			for i in l:
				for j in i:
					lab_s = i[j]
			print(lab_s)
			if (rv):
				sql = "UPDATE grades SET laboratory_score = JSON_INSERT(laboratory_score,'$.l',%s)  where id_student=%s and id_subject=%s"
				data_tuple = (note[nr_nota], id_s, id_subject)
				nr_nota = nr_nota + 1
				cur.execute(sql, data_tuple)
				mysql.connection.commit()
			else:
				x = {}
				x[nr_lab] = note[nr_nota]
				nr_nota = nr_nota + 1
				laboratory_score = json.dumps(x)
				# laboratory_score=grade
				cur.execute(
					"INSERT INTO grades (id_student, id_subject,grade_date,laboratory_score) VALUES ('" +
					str(id_s) + "', '" +
					str(id_subject) + "', '" +
					str(date.today()) + "', '" +
					str(laboratory_score) + "')")
				rv = cur.fetchall()
				mysql.connection.commit()
	else:
		if str(tip_note) == "Test Laborator":
			for id_s in students:
				print("ID STUDENT", id_s)
				# sql = "SELECT homework from grades where id_student=%s and id_subject=%s"
				# data_tuple = (id_s, id_subject)
				# cur.execute(sql, data_tuple)
				cur.execute("SELECT id_student from grades where id_student=%s and id_subject=%s", [id_s, id_subject])
				rv = cur.fetchall()
				l = []
				lab_s = ""
				for i in rv:
					l.append(i)
				for i in l:
					for j in i:
						lab_s = i[j]
				print(lab_s)
				if (lab_s):
					sql = "UPDATE grades SET laboratory_score = JSON_INSERT(laboratory_score,'$.l',%s)  where id_student=%s and id_subject=%s"
					data_tuple = (note[nr_nota], id_s, id_subject)
					nr_nota = nr_nota + 1
					cur.execute(sql, data_tuple)
					mysql.connection.commit()
				else:
					x = {}
					x[nr_lab] = note[nr_nota]
					nr_nota = nr_nota + 1
					laboratory_score = json.dumps(x)
					# laboratory_score=grade
					cur.execute(
						"INSERT INTO grades (id_student, id_subject,grade_date,laboratory_score) VALUES ('" +
						str(id_s) + "', '" +
						str(id_subject) + "', '" +
						str(date.today()) + "', '" +
						str(laboratory_score) + "')")
					rv = cur.fetchall()
					mysql.connection.commit()
		else:
			if str(tip_note) == "Tema":
				for id_s in students:
					print("ID STUDENT",id_s)
					cur.execute("SELECT id_student from grades where id_student=%s and id_subject=%s", [id_s,id_subject])
					rv = cur.fetchall()
					l = []
					lab_s = ""
					for i in rv:
						l.append(i)
					for i in l:
						for j in i:
							lab_s = i[j]
					print(lab_s)

					if(lab_s):
						sql = "UPDATE grades SET homework = JSON_INSERT(homework,'$.l',%s)  where id_student=%s and id_subject=%s"
						data_tuple = (note[nr_nota], id_s, id_subject)
						nr_nota = nr_nota + 1
						cur.execute(sql, data_tuple)
						mysql.connection.commit()
					else:
						x = {}
						x[nr_lab] = note[nr_nota]
						nr_nota = nr_nota + 1
						homework = json.dumps(x)
						# laboratory_score=grade
						cur.execute(
							"INSERT INTO grades (id_student, id_subject,grade_date,homework) VALUES ('" +
							str(id_s) + "', '" +
							str(id_subject) + "', '" +
							str(date.today()) + "', '" +
							str(homework) + "')")
						rv = cur.fetchall()
						mysql.connection.commit()

			else:
				if str(tip_note) == "Examen":
					for id_s in students:
						#sql = "SELECT exam from grades where id_student=%s and id_subject=%s"
						#data_tuple = (id_s, id_subject)
						#cur.execute(sql, data_tuple)
						cur.execute("SELECT id_student from grades where id_student=%s and id_subject=%s",[id_s,id_subject])
						rv = cur.fetchall()
						l = []
						lab_s = ""
						for i in rv:
							l.append(i)
						for i in l:
							for j in i:
								lab_s = i[j]
						print("XXXX",lab_s)
						if (lab_s):
							sql = "UPDATE grades SET exam = %s  where id_student=%s and id_subject=%s"
							data_tuple = (note[nr_nota], id_s, id_subject)
							nr_nota = nr_nota + 1
							cur.execute(sql, data_tuple)
							mysql.connection.commit()
						else:
							exam = note[nr_nota]
							cur.execute(
								"INSERT INTO grades (id_student, id_subject,grade_date,exam) VALUES ('" +
								str(id_s) + "', '" +
								str(id_subject) + "', '" +
								str(date.today()) + "', '" +
								str(exam) + "')")
							rv = cur.fetchall()
							mysql.connection.commit()
				else:
					if str(tip_note) == "Partial":
						for id_s in students:
							#sql = "SELECT partial from grades where id_student=%s and id_subject=%s"
							#data_tuple = (id_s, id_subject)
							#cur.execute(sql, data_tuple)
							cur.execute("SELECT id_student from grades where id_student=%s and id_subject=%s", [id_s,id_subject])
							rv = cur.fetchall()
							l = []
							lab_s = ""
							for i in rv:
								l.append(i)
							for i in l:
								for j in i:
									lab_s = i[j]
							print(lab_s)
							if (lab_s):
								sql = "UPDATE grades SET partial = %s  where id_student=%s and id_subject=%s"
								data_tuple = (note[nr_nota], id_s, id_subject)
								nr_nota = nr_nota + 1
								cur.execute(sql, data_tuple)
								mysql.connection.commit()
							else:
								partial = note[nr_nota]
								cur.execute(
									"INSERT INTO grades (id_student, id_subject,grade_date,partial) VALUES ('" +
									str(id_s) + "', '" +
									str(id_subject) + "', '" +
									str(date.today()) + "', '" +
									str(partial) + "')")
								rv = cur.fetchall()
								mysql.connection.commit()
					else:
						if str(tip_note) == "Bonus":
							for id_s in students:
								#sql = "SELECT bonus from grades where id_student=%s and id_subject=%s"
								#data_tuple = (id_s, id_subject)
								#cur.execute(sql, data_tuple)
								cur.execute("SELECT id_student from grades where id_student=%s", [id_s])
								rv = cur.fetchall()
								l = []
								lab_s = ""
								for i in rv:
									l.append(i)
								for i in l:
									for j in i:
										lab_s = i[j]
								print(lab_s)
								if (lab_s):
									sql = "UPDATE grades SET bonus = %s  where id_student=%s and id_subject=%s"
									data_tuple = (note[nr_nota], id_s, id_subject)
									nr_nota = nr_nota + 1
									cur.execute(sql, data_tuple)
									mysql.connection.commit()
								else:

									bonus = note[nr_nota]
									cur.execute(
										"INSERT INTO grades (id_student, id_subject,grade_date,bonus) VALUES ('" +
										str(id_s) + "', '" +
										str(id_subject) + "', '" +
										str(date.today()) + "', '" +
										str(bonus) + "')")
									rv = cur.fetchall()
									mysql.connection.commit()

		cur.execute("SELECT formula from subjects where subject_name=%s",[materia])
		rv6=cur.fetchall()
		for i in rv6:
			formulaf=i.get("formula")
		print("formula inainte de eval:", formulaf)

		def separe(F, T, A, T_score, A_score):
			for i in range(1, int(T) + 1):
				a = "T" + str(i)
				if a in F:
					x = F.replace(a, str(T_score[str(i)]))
					F = x
			for j in range(1, int(A) + 1):
				b = "A" + str(j)
				if b in F:
					y = F.replace(b, str(A_score[str(j)]))
					F = y
			return F

		def cnt(F, id_student, materia):
			l = F.split("count")
			print("Split dupa count:", l)
			i = []
			for s in l:
				q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa count
				i.append(q)  # pun in lista primele paranteze de dupa fiecare count
			print("Lista cu primele paranteze de dupa fiecare count:", i)

			lista_rezultate = []
			print("caut pentru studentul", id_student)
			for j in i:
				if (j):
					if ("P" == j):
						caut = materia + " Laborator/Seminar"
						cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",
									[id_student, caut])
						rv = cur.fetchall()
						print("p lab", rv)
						for kk in rv:
							for j in kk:
								count_present = kk[j]
						print("numarul prezentelor la  Laborator/Seminar este: ", count_present)
						lista_rezultate.append(count_present)

					if ("PC" == j):
						caut = materia + " Curs"
						cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",
									[id_student, caut])
						rv = cur.fetchall()
						print("p curs", rv)
						for kk in rv:
							for j in kk:
								count_present = kk[j]
						print("numarul prezentelor la Curs este: ", count_present)
						lista_rezultate.append(count_present)

					if ("PCons" == j):
						caut = materia + " Consultatie"
						cur.execute("SELECT COUNT(*) FROM presents WHERE id_student = %s and subject LIKE %s",
									[id_student, caut])
						rv = cur.fetchall()
						for kk in rv:
							for j in kk:
								count_present = kk[j]
						print("numarul prezentelor la Consultatii este: ", count_present)
						lista_rezultate.append(count_present)

			print("Lista rezultate expresii cu count:", lista_rezultate)
			print("F initial:", F)

			# daca lista e goala, sa o umplem cu 0
			# print(i)
			# x = F.replace("count("+ i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
			# print("Replace doar la prima paranteza:", x)
			del (i[0])
			# print(i)
			for m in range(0, len(lista_rezultate)):
				for k in range(m, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
					print("Parantezele pe care le caut:", "count(" + i[k] + ")")
					F = F.replace("count(" + i[k] + ")", str(lista_rezultate[m]))
					break  # inlocuiesc counturile urile pe care le gasesc
			print("Replace la tot da: ", F)
			return F

		def avg(F, scoreT, scoreH, scoreA, E):
			cur = mysql.connection.cursor()
			cur.execute("SELECT prop from subjects where subject_name=%s", [materia])
			rv = cur.fetchall()
			for i in rv:
				x = i.get("prop")
			prop1 = re.findall(r'\b\d+\b', x)
			T = prop1[0]
			H = prop1[1]
			A = prop1[2]
			l = F.split("avg")
			print("Split dupa avg:", l)
			i = []
			for s in l:  # parcurg lista cu splitul dupa avg
				q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa avg
				i.append(q)  # pun in lista primele paranteze de dupa fiecare avg
			print("Lista cu primele paranteze de dupa fiecare avg:", i)
			lista_rezultate = []
			for j in i:
				if (j):
					if ("A" in j):  # de preluat din bd jsonul de A
						suma = sum(scoreA.values())
						nr_laboratoare = int(A)
						media_laborator = suma / float(nr_laboratoare)
						lista_rezultate.append(media_laborator)
					else:
						if ("H" in j):  # de preluat din bd jsonul de H
							suma = sum(scoreH.values())
							nr_teme = int(H)
							media_laborator = suma / float(nr_teme)
							lista_rezultate.append(media_laborator)
						else:
							if ("T" in j):  # de preluat din bd jsonul de T
								suma = sum(scoreT.values())
								print("BAAFSFSDFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:", suma)
								nr_tl = int(T)
								print(nr_tl)
								media_laborator = suma / float(nr_tl)
								print(media_laborator)
								lista_rezultate.append(media_laborator)
							else:
								count_plusuri = j.count("+")
								count_plusuri += 1
								lista_rezultate.append((eval(j) / float(count_plusuri)))
			print("Lista rezultate expresii cu avg:", lista_rezultate)
			print("F initial:", F)

			x = F.replace("avg(" + i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
			print("Replace doar la prima paranteza:", x)

			for m in range(1, len(lista_rezultate)):
				for k in range(1, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
					print("Parantezele pe care le caut:", "avg(" + i[k] + ")")
					x = x.replace("avg(" + i[k] + ")",
								  str(lista_rezultate[m]))  # inlocuiesc avg urile pe care le gasesc

				print("Replace la tot: ", x)
			# print("Nota: ",eval(x))
			return x

		import math
		def final_grade(N, aprox_fgrade, materia, cati_studenti):

			if N <= 4.5:
				return 4
			grades = []
			if (aprox_fgrade == "Aproximare prin adaos"):
				if (N - math.floor(N) >= 0.5):
					return math.ceil(N)
				else:
					return math.floor(N)
			else:
				if (aprox_fgrade == "Aproximare prin trunchiere"):
					return math.floor(N)
				else:
					if (aprox_fgrade == "Gauss"):
						cur = mysql.connection.cursor()
						cur.execute("SELECT grade from finalgrades where subject=%s order by grade desc", [materia])
						rv = cur.fetchall()
						lista_note_studenti = []
						for i in rv:
							lista_note_studenti.append(float(i.get("grade")))
						s = cati_studenti
						grade10 = s * 0.05
						grade9 = s * 0.1
						grade8 = s * 0.2
						grade7 = s * 0.3
						grade6 = s * 0.2
						grade5 = s * 0.1
						grades.append(math.ceil(grade10))
						grades.append(math.ceil(grade9))
						grades.append(math.ceil(grade8))
						grades.append(math.ceil(grade7))
						grades.append(math.ceil(grade6))
						grades.append(math.ceil(grade5))
						print("Cati o sa aiba 10 9 ..", grades)
						nota_actuala = 10
						noua_lista = []
						print("NOTE BD", lista_note_studenti)
						for i in grades:
							for ceva in range(0, i):
								noua_lista.append(nota_actuala)
							nota_actuala = nota_actuala - 1
						print("noua listaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", noua_lista)
						pos = 0
						for i in range(0, len(lista_note_studenti)):
							if lista_note_studenti[i] == round(N, 1) or (
									lista_note_studenti[i] >= round(N, 1) and lista_note_studenti[i + 1] <= round(N,1)):
								pos = i
								print("Pozitia notei in lista descrescatoare: ", pos)
								break
						print(pos)
						return noua_lista[pos]


		def suma(F, scoreT, scoreH, scoreA):
			l = F.split("sum")
			print("Split dupa sum:", l)
			i = []
			for s in l:  # parcurg lista cu splitul dupa avg
				q = s[s.find("(") + 1:s.find(")")]  # salvez ce e in prima paranteza dupa avg
				i.append(q)  # pun in lista primele paranteze de dupa fiecare avg
			print("Lista cu primele paranteze de dupa fiecare sum:", i)
			lista_rezultate = []
			for j in i:
				if (j):
					if ("A" in j):
						lista_rezultate.append(sum(scoreA.values()))  # de preluat din bd jsonul de A
					else:
						if ("H" in j):
							lista_rezultate.append(sum(scoreH.values()))  # de preluat din bd jsonul de H
						else:
							if ("T" in j):
								lista_rezultate.append(sum(scoreT.values()))  # de preluat din bd jsonul de T

			print("Lista rezultate expresii cu sum:", lista_rezultate)
			print("F initial:", F)
			x = F.replace("sum(" + i[1] + ")", str(lista_rezultate[0]))  # aici fac replace la prima paranteza
			print("Replace doar la prima paranteza:", x)
			for m in range(1, len(lista_rezultate)):
				for k in range(1, len(i)):  # parcurg lista cu parantezele si le caut in formula principala
					print("Parantezele pe care le caut:", "sum(" + i[k] + ")")
					x = x.replace("sum(" + i[k] + ")",
								  str(lista_rezultate[m]))  # inlocuiesc avg urile pe care le gasesc

				print("Replace la tot: ", x)
			return x

		cur = mysql.connection.cursor()
		cur.execute("SELECT prop from subjects where subject_name=%s", [materia])
		rv = cur.fetchall()
		for i in rv:
			x = i.get("prop")
		prop1 = re.findall(r'\b\d+\b', x)
		T = prop1[0]
		H = prop1[1]
		A = prop1[2]

		for i in students:
			E = 0
			print("STUDENTUL: ", i)
			if "E" in formulaf:
				cur.execute("SELECT exam from grades where id_student=%s and id_subject=%s", [i, id_subject])
				rv = cur.fetchall()
				if not rv:
					E = 0
				else:
					for ip in rv:
						if ip != None:
							E = ip.get("exam")
			# print("E",E)
			if "PR" in formulaf:
				cur.execute("SELECT partial from grades where id_student=%s and id_subject=%s", [i, id_subject])
				rv = cur.fetchall()
				if not rv:
					PR = 0
				else:
					for ip in rv:
						if ip != None:
							PR = ip.get("partial")
			# print("PR", PR)

			if "PJ" in formulaf:
				cur.execute("SELECT project from grades where id_student=%s and id_subject=%s", [i, id_subject])
				rv = cur.fetchall()
				if not rv:
					PJ = 0
				else:
					for ip in rv:
						if ip != None:
							PJ = ip.get("project")
			# print("PJ", PJ)

			cur.execute("SELECT laboratory_score from grades where id_student=%s and id_subject=%s", [i, id_subject])
			rv = cur.fetchall()
			if len(rv) == 0:
				scoreA = {}
				for k in range(1, int(T) + 1):
					scoreA[str(k)] = 0
			else:
				for j in rv:
					A_score = j.get("laboratory_score")
					if (A_score != None):
						scoreA = json.loads(A_score)
					else:
						scoreA = {}
						for k in range(1, int(A) + 1):
							scoreA[str(k)] = 0
			# print("scoreA",scoreA)

			cur.execute("SELECT laboratory_test from grades where id_student=%s and id_subject=%s", [i, id_subject])
			rv = cur.fetchall()
			if len(rv) == 0:
				scoreT = {}
				for k in range(1, int(T) + 1):
					scoreT[str(k)] = 0
			else:
				for j in rv:
					T_score = j.get("laboratory_test")
					print("TTTTTTTTTTTTT", T_score)
					if (T_score != None):
						scoreT = json.loads(T_score)
					else:
						scoreT = {}
						for k in range(1, int(T) + 1):
							scoreT[str(k)] = 0
			print("scoreT", scoreT)

			cur.execute("SELECT homework from grades where id_student=%s and id_subject=%s", [i, id_subject])
			rv = cur.fetchall()
			if len(rv) == 0:
				scoreH = {}
				for k in range(1, int(T) + 1):
					scoreH[str(k)] = 0
			else:
				for j in rv:
					H_score = j.get("homework")
					if (H_score != None):
						scoreH = json.loads(H_score)
					else:
						scoreH = {}
						for k in range(1, int(H) + 1):
							scoreH[str(k)] = 0

			Nou = separe(formulaf, T, A, scoreT, scoreA)
			if "count" in Nou:
				z = cnt(Nou, i, materia)
				F = z

			if "avg" in Nou:
				x = avg(Nou, scoreT, scoreH, scoreA, E)
				print("x actual: ", x)
				Nou = x
				if "sum" in x:
					y = suma(x, scoreT, scoreH, scoreA)
					print("y actual: ", y)
					F = y
			else:
				if "avg" not in Nou and "sum" in Nou:
					y = suma(Nou, scoreT, scoreH, scoreA)
					F = y

			print("formula inainte de eval:", formulaf)
			N=eval(Nou)
			trecut = 1
			cond = ""
			cur.execute("SELECT * from finalgrades where id_student=%s and subject=%s", [i, materia])
			rv100 = cur.fetchall()
			if (rv100):
				cur.execute("UPDATE finalgrades set grade=%s WHERE id_student=%s and subject=%s", [N, i, materia])
				mysql.connection.commit()
			else:
				cur.execute(
					"INSERT INTO finalgrades (id_student,subject,grade) VALUES ('" +
					str(i) + "', '" +
					str(materia) + "', '" +
					str(N) + "')")
				mysql.connection.commit()
			cur.execute("SELECT aprox_fgrade from subjects where subject_name=%s",[materia])
			ooo = cur.fetchall()
			for q in ooo:
				aprox_fgrade=q.get("aprox_fgrade")
			cati_studenti=len(students)
			NFinal = final_grade(N, aprox_fgrade, materia, cati_studenti)

			mysql.connection.cursor()
			print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK", NFinal, i, materia)
			cur.execute("UPDATE finalgrades set finalgrade=%s WHERE id_student=%s and subject=%s", [NFinal, i, materia])
			mysql.connection.commit()
			print("GATA")

	result = jsonify({"response": "Note trimise cu succes!"})
	return result


if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1', ssl_context=context)


