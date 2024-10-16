import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID  # Use for PostgreSQL
from sqlalchemy import func
from sqlalchemy import Enum
import enum


# Define an enumeration for the categories
class DepositFromEnum(enum.Enum):
    chips = "Chips"
    bar = "Bar"
    poolTable = "Pool Table"


class Deposit(db.Model):
    __tablename__ = 'mobile_money_deposits'

    # Using UUID for the primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_of_deposit = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=func.current_date())

    # Add category as an Enum
    deposit_from = db.Column(Enum(DepositFromEnum), nullable=False)

