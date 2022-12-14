from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from instance import config
from sqlalchemy.pool import NullPool


db_drive = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (config.DB_ID, \
    config.DB_PW, config.DB_HOST, config.DB_PORT, config.DB_DATABASE)                                           

engine = create_engine(db_drive, encoding='utf-8', echo=True, \
    poolclass=NullPool, isolation_level="READ UNCOMMITTED", convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import model
    Base.metadata.create_all(bind=engine)


