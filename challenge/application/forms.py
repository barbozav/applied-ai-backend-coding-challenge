from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):
    """A simple form for requesting a translation."""

    method = SelectField(
        'Translation Method',
        choices=[('mt', 'Marian-NMT Server Automated Translation'),
                 ('api', "Unbabel's API Manual Translation")])

    text = TextAreaField(
        '',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter here a text to be translated."})

    submit = SubmitField('Translate')
