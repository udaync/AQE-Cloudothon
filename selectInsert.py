import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:6543/lecture"

engine = create_engine('postgresql://postgres:postgres@localhost:6543/lecture')
engine.connect()
db = scoped_session(sessionmaker(bind=engine))

query = "select origin, destination, duration from flights"


def main():
    flights = db.execute(query).fetchall()
    """print (flights)"""
    for flights in flights:
        print(f"Origin: {flights.origin},Destination: {flights.destination},duration: {flights.duration}")


if __name__ == "__main__":
    main()
