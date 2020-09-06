from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, session
import requests


app = Flask(__name__)
app.secret_key = 'abcdefghijkl'
engine = create_engine('postgresql://postgres:postgres@localhost:5432/lecture')
engine.connect()
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template("welcome.html", message_success="Logged in as", username=username)
    return render_template("index1.html", message="Login form")


@app.route("/login", methods=["POST"])
def login():
    temp_username = request.form.get("username")
    username = temp_username.lower()
    password = str(request.form.get("password"))
    if db.execute("SELECT username from userdata where username = :username", {"username": username}).rowcount == 0:
        return render_template("index1.html", message_alert="Username Not Exist!")
    elif password != db.execute("SELECT password from userdata where username = :username", {"username": username}).fetchone()[0]:
        return render_template("index1.html", message_alert="Wrong Credentials!")
    else:
        """ Temporary Code """
        session['username'] = username
        return render_template("welcome.html", message_success="Welcome", username=username)


@app.route("/registration")
def registration():
    return render_template("registration.html", message="Please fill your details !")


@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        temp_username = request.form.get("username")
        temp_email = request.form.get("email")
        email = temp_email.lower()
        username = temp_username.lower()
        password = request.form.get("password")

        if fname == "" or lname == '' or email == "" or username == "" or password == "":
            return render_template("registration.html", message_alert="Please fill all fields")
        if db.execute("SELECT username from userdata where username = :username", {"username" : username}).rowcount != 0:
            return render_template("registration.html", message_alert="username already exist")
        if db.execute("SELECT email from userdata where email = :email", {"email" : email}).rowcount != 0:
            return render_template("registration.html", message_alert="Your Email already Registered")
        db.execute("INSERT INTO userdata (fname, lname, email, username, password) VALUES (:fname,:lname, :email,\
            :username,:password)",{"fname": fname, "lname": lname, "email": email, "username": username, "password": password})
        db.commit()
        return render_template("index.html", message_success="Registration Successful , Login Now")
    return render_template("registration.html", message="Please fill your details !")


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        temp_query = request.form.get("query")
        if len(str(temp_query)) < 4:
            return render_template('welcome.html', message="Search query should have at least 4 character")
        else:
            query = "%" + str(temp_query) + "%"
            """ Search in ISBN of book"""
            result_isbn = db.execute("SELECT * from books where ISBN ilike :isbn", {"isbn": query}).fetchall()
            """ Search in TITLE of book"""
            result_title = db.execute("SELECT * from books where TITLE ilike :title", {"title": query}).fetchall()
            """ Search in AUTHOR """
            result_author = db.execute("SELECT * from books where AUTHOR ilike :author", {"author": query}).fetchall()
            final_result = result_isbn + result_title + result_author
            count = len(final_result)
            if count == 0:
                return render_template('welcome.html', message="No Result found for:", temp_query=temp_query)
            else:
                return render_template('welcome.html', message="Below is your search result for", final_result=final_result,
                                    temp_query=temp_query, count=count, message_count="Total book found: ")
    else:
        return render_template("index.html", message="Please fill you login Credentials")


@app.route("/details/<book_isbn>", methods=["POST", "GET"])
def details(book_isbn):
        isbng= "9780" + book_isbn
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "bQKzlniXrllUVaG8EHEkIQ", "isbns": isbng})
        if request.method == "GET":
            book_detail = db.execute("select * from books where isbn = :isbn", {"isbn": book_isbn}).fetchall()
            book_reviews = db.execute("select * from book_review where isbn = :isbn", {"isbn": book_isbn}).fetchmany(size=10)
            return render_template('details.html', message="Details of selected book", book_detail=book_detail,
                                   book_reviews=book_reviews, res=res)
        else:
            try:
                rating = request.form.get("rating")
            except ValueError:
                return render_template("error.html", message="Some Problem in Rating Input")
            else:
                username = str(session['username'])
                if rating == "" or rating == "Rate the Book":
                    rating = "No Rating submitted for this book"
                elif db.execute("select * from book_rating where isbn = :isbn and username = :username",
                              {"isbn": book_isbn, "username": username}).rowcount > 0:
                    rating = "You already submitted rating for this book before"
                else:
                    db.execute("INSERT INTO book_rating (ISBN, username, rating) VALUES (:isbn, :username, :rating)",
                               {"isbn": book_isbn, "username": username, "rating": rating})
            finally:
                db.commit()
            review = request.form.get("review")
            if review == "":
                review = "No Review submitted for this book"
            elif db.execute("select * from book_review where isbn = :isbn and username = :username",
                            {"isbn": book_isbn, "username": username}).rowcount > 0:
                review = "You already submitted review for this book before"
            else:
                db.execute("INSERT INTO book_review (ISBN, username, review) VALUES (:isbn, :username, :review)",
                           {"isbn": book_isbn, "username": username, "review": review})
                db.commit()
            return render_template('final.html', message="Thanks for Review!!", rating=rating, review=review)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return render_template("index1.html", message="Logout Successful")


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80)






