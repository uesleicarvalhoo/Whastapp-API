from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import SQLALCHEMY_DB_URI

db = create_engine(SQLALCHEMY_DB_URI)
session = sessionmaker(db, autocommit=False)()
