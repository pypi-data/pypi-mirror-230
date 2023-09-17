# Conexión a Base de Datos y manejo de datos
# Creado por: Totem Bear
# Fecha: 23-Ago-2023

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# POSTGRESQL
def set_db_params(dbengine, dbuser, dbpass, dbhost, dbport, dbname, autocommit, autoflush):
    SQLALCHEMY_DATABASE_URL = dbengine + "://" + dbuser + ":" + dbpass + dbhost + ":" + dbport + "/" + dbname
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=engine)
    Base = declarative_base()

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

    return dict(sql_url=SQLALCHEMY_DATABASE_URL, engine=engine, SessionLocal=SessionLocal, Base=Base, db=db)
