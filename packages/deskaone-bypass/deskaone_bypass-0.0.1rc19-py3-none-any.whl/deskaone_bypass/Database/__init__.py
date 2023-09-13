import sqlalchemy as db, os, json, time
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, InterfaceError, OperationalError



from deskaone_bypass.Exceptions import DatabaseError

class Database:
    
    BASE = declarative_base()
    
    def __init__(self, DATABASE_URL: str) -> None:
        __engine      = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        __metadata    = MetaData()
        TRY = 0
        while True:
            TRY += 1
            try: self.Connect = __engine.connect(); break
            except KeyboardInterrupt: exit()
            except OperationalError as e: 
                if TRY >= 5: raise DatabaseError(str(e))
                time.sleep(5);print(e)
        self.BASE.metadata.create_all(__engine)
        self.Engine      = __engine
        self.Metadata    = __metadata

