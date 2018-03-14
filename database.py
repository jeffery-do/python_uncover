import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

user = os.environ['POSTGRES_USER']
pwd = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DB']
print("info",user, pwd, db)
# host = 'db'
host = 'db:5432'
# port = '5432'
print("engine string", ('postgresql+psycopg2://%s:%s@%s/%s' % (user, pwd, host, db)))
db_engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (user, pwd, host, db))
db_session = None

def open_session():
    global db_session
    db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db_engine))
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=db_engine)

open_session()

Base = declarative_base()
Base.query = db_session.query_property()
