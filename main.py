from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

#Database 
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@db/mydb"

#SQLAlchemy
Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Model for counting requests
class RequestCount(Base):
    __tablename__ = "request_count"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)

# Initializing database
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_db():
    try:
        db = SessionLocal()
        # Check if the table exists; if not, create the initial row
        if db.query(RequestCount).count() == 0:
            db.add(RequestCount(count=0))
            db.commit()
    except SQLAlchemyError as e:
        print(f"Error during database initialization: {e}")
    finally:
        db.close()

@app.get("/count")
def get_count():
    db = SessionLocal()
    count_record = db.query(RequestCount).first()
    db.close()
    return {"count": count_record.count}

@app.middleware("http")
async def count_requests(request, call_next):
    db = SessionLocal()
    count_record = db.query(RequestCount).first()
    count_record.count += 1
    db.commit()
    db.close()
    response = await call_next(request)
    return response

