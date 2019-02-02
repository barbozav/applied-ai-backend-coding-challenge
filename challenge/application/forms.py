from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):
    """A simple form for requesting a translation."""

    method = SelectField(
        'Translation Method', choices=[('mt', 'Automatic'), ('api', 'Manual')])

    text = TextAreaField(
        '',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter here a text to be translated."})

    submit = SubmitField('Translate')
