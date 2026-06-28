from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ReimbursementRecord(Base):
    __tablename__ = "reimbursement_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_code = Column(String(255), nullable=True)
    item_name = Column(String(255), nullable=True)
    category_code = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    expense_type = Column(String(255), nullable=True)
    period_1_2 = Column(String(255), nullable=True)
    payment_method = Column(String(255), nullable=True)
    business_trip = Column(String(255), nullable=True)
    travel_expense = Column(String(255), nullable=True)
    meal_expense = Column(String(255), nullable=True)
    lodging_expense = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    group_name = Column(String(255), nullable=True)


DB_PATH = "sqlite:///reimbursement.db"
engine = create_engine(DB_PATH, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
