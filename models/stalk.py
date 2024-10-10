import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID  # Use for PostgreSQL
from sqlalchemy import func
from sqlalchemy import Enum
import enum


# Define an enumeration for the categories
class CategoryEnum(enum.Enum):
    soda = "Soda"
    beer = "Beer"
    spirits = "Spirits"
    water = "Water"
    energy_drink = "Energy Drink"
    other = "Other"


class Item(db.Model):
    __tablename__ = 'items'

    # Using UUID for the primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=func.current_date())

    # Add category as an Enum
    category = db.Column(Enum(CategoryEnum), nullable=False)


class StockRecord(db.Model):
    __tablename__ = 'stock_records'

    # Using UUID for the primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    # Foreign key references the UUID of the Item
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey('items.id'), nullable=False)

    old_stalk = db.Column(db.Integer, nullable=False)
    current_stalk = db.Column(db.Integer, nullable=False)
    new_stalk = db.Column(db.Integer, nullable=True)
    sales = db.Column(db.Integer, nullable=True)
    cash = db.Column(db.Float, nullable=True)

    # Relationship to retrieve the associated item
    item = db.relationship('Item')

    def calculate_sales(self):
        return self.old_stalk - self.current_stalk

    def calculate_cash(self):
        return self.calculate_sales() * self.item.price
