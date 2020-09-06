import os
import psycopg2
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgresql://postgres:postgres@localhost:5432/lecture')
engine.connect()
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for i, t, a, y in reader:
        db.execute("INSERT INTO books (isbn,title,author,pubyear) VALUES (:isbn,:title,:author,:pubyear)",
                   {"isbn": i, "title": t, "author": a, "pubyear": y})
        db.commit()


if __name__ == "__main__":
    main()
