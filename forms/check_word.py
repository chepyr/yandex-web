from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CheckWordLine(FlaskForm):
    word_line = StringField(validators=[DataRequired()])
    submit = SubmitField('Проверить')
