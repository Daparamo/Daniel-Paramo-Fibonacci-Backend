from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Fibonacci(Base):
  __tablename__ = "fibonacci"
  id = Column(Integer, primary_key=True)
  fecha = Column(DateTime)
  fibonacci=Column(String)