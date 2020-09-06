from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, session

engine = create_engine('postgresql://postgres:postgres@localhost:6543/lecture')
engine.connect()
db = scoped_session(sessionmaker(bind=engine))

query = "%394758%"

""" Search in ISBN of book"""
result_isbn = db.execute("SELECT * from books where ISBN like :isbn", {"isbn": query}).fetchall()
""" Search in TITLE of book"""
result_title = db.execute("SELECT * from books where TITLE like :title", {"title": query}).fetchall()
""" Search in AUTHOR """
result_author = db.execute("SELECT * from books where AUTHOR like :author", {"author": query}).fetchall()

temp_result = result_isbn + result_title + result_author

final_result = []

""""" Converting resultproxy(list of result proxy) to list of lists """"
for book in temp_result:
    temp = []
    print(book)
    for item in range(len(book)):
        temp.append(book[item])
    final_result.append(temp)

for book in temp_result:
    print(book)
    for isbn, title, author, pubyear in book:
        print(f"ISBN : {isbn}")
        print(f"Title : {title}")
        print(f"Author : {author}")
        print(f"Publish Year  : {pubyear}")