import sqlalchemy as db, os, json, time, random
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
        TRY = 0
        while True:
            __engine      = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
            __metadata    = MetaData()
            TRY += 1
            try: 
                print(f'trying Connection in Database {TRY}', end='\r')
                self.Connect = __engine.connect()
                self.BASE.metadata.create_all(__engine)
                self.Engine      = __engine
                self.Metadata    = __metadata
                break
            except KeyboardInterrupt: exit()
            except OperationalError as e: 
                if TRY >= 1000: raise DatabaseError(str(e))
                time.sleep(random.randint(5, 30))
        

