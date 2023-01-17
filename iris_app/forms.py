from flask_wtf import FlaskForm
from wtforms import DecimalField
from wtforms.validators import DataRequired


class PredictionForm(FlaskForm):
    """Fields to a form to input the values required for an iris species prediction"""

    # https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.DecimalField
    sepal_length = DecimalField(validators=[DataRequired()])
    sepal_width = DecimalField(validators=[DataRequired()])
    petal_length = DecimalField(validators=[DataRequired()])
    petal_width = DecimalField(validators=[DataRequired()])
