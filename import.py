import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_string="postgres://fugrvrrzhvxkvi:96157545cd92a964d7c6ff59f3e4937a41b3c73dd9e0978961ff1b4ae64bd4d6@ec2-3-231-16-122.compute-1.amazonaws.com:5432/dd93fq5jct6or3"
db = scoped_session(sessionmaker(bind=create_engine(db_string)))

f=open("books.csv")

reader=csv.reader(f)
l=0
for isbn, title, author, year in reader:
	if l==0:
		l+=1
	else:
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,  :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
		l+=1
		print(f"{l-1}.\tAdded to Database: {title}")

db.commit()

