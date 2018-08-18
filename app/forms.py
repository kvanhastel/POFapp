from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, InputRequired
from app.models import Gebruiker, Ploeg
from app import Config

class LoginForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[DataRequired(message="Geen gebruikersnaam opgegeven")])
    password = PasswordField('Paswoord', validators=[DataRequired(message="Geen paswoord opgegeven")])
    remember_me = BooleanField('Onthoud')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[DataRequired(message="Geen gebruikersnaam opgegeven")])
    name = StringField('Naam', validators=[DataRequired(message="Geen naam opgegeven")])
    password = PasswordField('Paswoord', validators=[DataRequired(message="Geen paswoord opgegeven")])
    password2 = PasswordField(
        'Herhaal Paswoord', validators=[DataRequired(message="Geen paswoord controle opgegeven"),
                                        EqualTo('password', message="Wachtwoorden zijn niet hetzelfde")])
    rechten = RadioField('Rechten', choices=[('administrator','Administrator'),('werkgroep','Werkgroep'),('ploegkapitein','Ploegkapitein')],
                         validators=[InputRequired(message="Geen keuze gemaakt")])
    submit = SubmitField('Maak gebruiker aan')

    def validate_username(self, username):
        user = Gebruiker.query.filter_by(gebruikersnaam=username.data).first()
        if user is not None:
            raise ValidationError('Gebruikersnaam al in gebruik. Kies een andere gebruikersnaam.')


class BasisloegenForm(FlaskForm):


    lijst_ploegen = []
    i=1
    query_ploegen = Ploeg.query.all()
    for ploeg in query_ploegen:
        lijst_ploegen.append((str(i), ploeg.ploegnaam))
        i = i+1

    seizoenen = SelectField('seizoen', choices=Config.SEIZOENEN, validators=[InputRequired(message="Geen seizoen opgegeven")])
    competities = SelectField('competities', choices=Config.COMPETITIES, validators=[InputRequired(message="Geen competitie opgegeven")])
    ploegen = SelectField('ploegen', choices=lijst_ploegen,
                              validators=[InputRequired(message="Geen ploeg geselecteerd")])
    '''
    seizoenen = StringField('ploegnaam', validators=[DataRequired(message="Geen seizoen opgegeven")])
    ploegnaam = StringField('ploegnaam', validators=[DataRequired(message="Geen ploegnaam opgegeven")])
    basisspeler1 = StringField('speler1', validators=[DataRequired(message="Geen basisspeler opgegeven")])
    basisspeler2 = StringField('speler2', validators=[DataRequired(message="Geen basisspeler opgegeven")])
    basisspeler3 = StringField('speler3', validators=[DataRequired(message="Geen basisspeler opgegeven")])
    basisspeler4 = StringField('speler4', validators=[DataRequired(message="Geen basisspeler opgegeven")])
    '''
'''
class PloegopstellingForm(FlaskForm):

'''