from app import db
from models.stalk import Item


def create_item(item_name, buying_price, selling_price, category):
    new_item = Item(name=item_name, buying_price=buying_price, selling_price=selling_price, category=category)
    db.session.add(new_item)
    db.session.commit()


def get_items():
    return Item.query.all()
