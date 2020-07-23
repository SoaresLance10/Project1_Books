import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
db_string="postgres://fugrvrrzhvxkvi:96157545cd92a964d7c6ff59f3e4937a41b3c73dd9e0978961ff1b4ae64bd4d6@ec2-3-231-16-122.compute-1.amazonaws.com:5432/dd93fq5jct6or3"
db = scoped_session(sessionmaker(bind=create_engine(db_string)))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = str(request.form.get("username"))
    password = str(request.form.get("password"))
    if db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).rowcount == 0:
    	return render_template("error.html", message="Username or Password Incorrect. Please try Again.")
    else:
    	resultproxy = db.execute("SELECT * FROM users WHERE username=:username", {"username": username})
    	d, a = {}, []
    	for rowproxy in resultproxy:
    		# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
    		for column, value in rowproxy.items():
    			# build up the dictionary
    			d = {**d, **{column: value}}
    		a.append(d)
    	p=list(a[0].values())[3]
    	if password==p:
    		return redirect(url_for('user', username=username))
    	else:
    		return render_template("error.html", message="Username or Password Incorrect. Please try Again.")
    	


@app.route("/signup", methods=["GET" , "POST"])
def signup():
	if request.method == 'GET':
		return render_template("signup.html")

	if request.method == 'POST':
		name = str(request.form.get("name"))
		username = str(request.form.get("username"))
		password = str(request.form.get("password"))
		rpassword = str(request.form.get("rpassword"))
		if db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).rowcount != 0: 
			return render_template("error.html", message="Username already taken. Please Try Again with another Username.")
		elif password != rpassword:
			return render_template("error.html", message="Password Re-Entered Incorrestly. Please Try Again.")
		else:
			db.execute("INSERT INTO users (username, name, password) VALUES (:username, :name, :password)", {"username": username, "name": name, "password": password})
			db.commit()
			return render_template("success.html", message="Account for "+name+" with Username "+username+" created Successfully. You may log into you account with the Username and password from the Home Page")


@app.route('/user/<username>', methods=["GET" , "POST"])
def user(username):
	if request.method == 'GET':
		if db.execute("SELECT * FROM reviews WHERE username=:username", {"username": username}).rowcount == 0:
			reviews='empty'
		else:
			resultproxy = results = db.execute("SELECT * FROM reviews WHERE username=:username", {"username": username}).fetchall();
			d, a = {}, []
			for rowproxy in resultproxy:
				# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
				for column, value in rowproxy.items():
					# build up the dictionary
					d = {**d, **{column: value}}
				a.append(d)

			reviews=[]
			for item in a:
				reviews.append(list(item.values()))

		return render_template("user.html", username=username, reviews=reviews)

	if request.method == 'POST':
		isbn=str(request.form.get("isbn"))
		title=str(request.form.get("title"))
		author=str(request.form.get("author"))

		if isbn!="":
			resultproxy = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn})
			d, a = {}, []
			for rowproxy in resultproxy:
				# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
				for column, value in rowproxy.items():
					# build up the dictionary
					d = {**d, **{column: value}}
				a.append(d)

		elif title!="":
			resultproxy = db.execute("SELECT * FROM books WHERE title LIKE :search", {"search": f"%{title}%"}).fetchall();
			d, a = {}, []
			for rowproxy in resultproxy:
				# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
				for column, value in rowproxy.items():
					# build up the dictionary
					d = {**d, **{column: value}}
				a.append(d)

		elif author!="":
			resultproxy = db.execute("SELECT * FROM books WHERE author LIKE :search", {"search": f"%{author}%"}).fetchall();
			d, a = {}, []
			for rowproxy in resultproxy:
				# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
				for column, value in rowproxy.items():
					# build up the dictionary
					d = {**d, **{column: value}}
				a.append(d)

			
		books=[]
		for item in a:
			books.append(list(item.values()))
		if books==[]:
			books='empty'

		return render_template("found.html", books=books, username=username)


@app.route('/book/<username>/<isbn>', methods=["GET" , "POST"])
def book(isbn, username):
	resultproxy = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn})
	d, a = {}, []
	for rowproxy in resultproxy:
		# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
		for column, value in rowproxy.items():
			# build up the dictionary
			d = {**d, **{column: value}}
		a.append(d)
	
	books=[]
	for item in a:
		books.append(list(item.values()))

	title=books[0][2]
	author=books[0][3]
	year=books[0][4]
	
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "M3XlTtlr9U9pLIKduCWGiQ", "isbns": f"{isbn}"})
	var=res.json()['books'][0]

	ratings_count=var['work_ratings_count']
	text_reviews_count=var['work_text_reviews_count']
	avg_rating=var['average_rating']

	resultproxy = db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND username=:username", {"isbn": isbn, "username": username})
	d, a = {}, []
	for rowproxy in resultproxy:
		# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
		for column, value in rowproxy.items():
			# build up the dictionary
			d = {**d, **{column: value}}
		a.append(d)
	
	reviews=[]
	for item in a:
		reviews.append(list(item.values()))

	if reviews==[]:
		reviews='empty'

	return render_template("book.html", isbn=isbn, title=title, author=author, year=year, username=username, ratings_count=ratings_count, 
		text_reviews_count=text_reviews_count, avg_rating=avg_rating, reviews=reviews)


@app.route("/review/<username>/<isbn>", methods=["GET","POST"])
def review(username, isbn):

	treview = str(request.form.get("treview"))
	rating = str(request.form.get("rating"))
	
	db.execute("INSERT INTO reviews (username, isbn, review, rating) VALUES (:username, :isbn, :review, :rating)", {"username": username, "isbn": isbn, "review": treview, "rating": rating})
	db.commit()

	return render_template("success.html", message=f"Successfully Added Review by {username} to our Database:")

@app.route("/api/<isbn>")
def api(isbn):
	resultproxy = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn})
	d, a = {}, []
	for rowproxy in resultproxy:
		# rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
		for column, value in rowproxy.items():
			# build up the dictionary
			d = {**d, **{column: value}}
		a.append(d)
	
	books=[]
	for item in a:
		books.append(list(item.values()))

	if books==[]:
		return jsonify({"error": "No Such Book Found in Database"}), 404
	else:
		return jsonify({
				"book_isbn": books[0][1],
				"book_title": books[0][2],
				"book_author": books[0][3],
				"book_publish_year": books[0][4],
			})