from app import db
from models.deposits import Deposit


def create_deposit(amount, date, deposit_from):
    new_deposit = Deposit(amount=amount, date_of_deposit=date, deposit_from=deposit_from)
    db.session.add(new_deposit)
    db.session.commit()


def get_deposits():
    return Deposit.query.all()
