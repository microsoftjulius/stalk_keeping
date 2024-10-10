from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from models.stalk import CategoryEnum


class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    buying_price = FloatField('Buying Price', validators=[DataRequired(), NumberRange(min=0)])
    selling_price = FloatField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])

    # Use a SelectField for category with predefined choices
    category = SelectField('Category', choices=[
        (CategoryEnum.soda.name, CategoryEnum.soda.value),
        (CategoryEnum.beer.name, CategoryEnum.beer.value),
        (CategoryEnum.spirits.name, CategoryEnum.spirits.value),
        (CategoryEnum.water.name, CategoryEnum.water.value),
        (CategoryEnum.energy_drink.name, CategoryEnum.energy_drink.value),
        (CategoryEnum.other.name, CategoryEnum.other.value)
    ], validators=[DataRequired()])

    submit = SubmitField('Submit')