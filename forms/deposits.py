from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired

from models.deposits import DepositFromEnum


class DepositForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    # Use a SelectField for deposit from with predefined choices
    deposit_from = SelectField('Deposit From', choices=[
        (DepositFromEnum.chips.name, DepositFromEnum.chips.value),
        (DepositFromEnum.bar.name, DepositFromEnum.bar.value),
        (DepositFromEnum.poolTable.name, DepositFromEnum.poolTable.value),
    ], validators=[DataRequired()])

    submit = SubmitField('Submit')