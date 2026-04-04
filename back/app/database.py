#!/usr/bin/env python3

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
ECHO = os.getenv('DATABASE_ECHO', 'False').lower() in ['true', '1', 'y', 'yes']

# Skip database initialization when running under pytest
# Tests will create their own engine via conftest.py
is_pytest = 'pytest' in sys.modules

if DATABASE_URL and not is_pytest:
    if not database_exists(DATABASE_URL):
        create_database(DATABASE_URL)

    engine = create_engine(
        DATABASE_URL,
        echo=ECHO
    )
else:
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

