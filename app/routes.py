from app import app
from flask import render_template, redirect, url_for, flash, request, json, jsonify, g
from app.forms import LoginForm, RegistrationForm, BasisloegenForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Gebruiker, Speler, Ploeg
from werkzeug.urls import url_parse
from app import db
from functools import wraps
from app import Config


def login_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rechten != "administrator":
            flash('geen rechten tot deze pagina')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def login_werkgroep_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rechten != "werkgroep" and current_user.rechten != "administrator":
            flash('geen rechten tot deze pagina')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def login_ploegkapitein_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('geen rechten tot deze pagina')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/ploegopstellingsformulier')
@login_ploegkapitein_required
def ploegopstellingsformulier():
    return render_template('ploegopstellingsformulier.html')


@app.route('/reservespelers')
@login_ploegkapitein_required
def reservespelers():
    return render_template('reservespelers.html')


# filter om alleen competitiespelers te selecteren
#spelers = Speler.query.all()

# filter om alleen recreanten te selecteren
 spelers = Speler.query.filter((Speler.role =='Speler') | (Speler.typename == 'recreant')).all()

# filter om alleen competitiespelers te selecteren
# spelers = Speler.query.filter((Speler.role =='Speler') | (Speler.role == 'Uitgeleende speler')).filter_by(website='http://www.interclub.be').all()

# filter om alleen competitiespelers te selecteren
spelers = Speler.query.filter((Speler.role =='Speler') | (Speler.role == 'Uitgeleende speler')).filter_by(website='http://www.interclub.be').all()

@app.route('/spelerslijst')
@login_ploegkapitein_required
def spelerslijst():
    return render_template('spelerslijst.html', spelers=spelers)


@app.route('/speler/<string:memberid>/')
@login_ploegkapitein_required
def speler(memberid):
        s = Speler.query.filter_by(memberid=memberid).first()
        return render_template('speler.html', s=s)

@app.route('/basisploegen')
@login_werkgroep_required
def basisploegen():
    seizoenen = Config.SEIZOENEN
    competities = Config.COMPETITIES
    form = BasisloegenForm()
    return render_template('basisploegen.html', form=form, seizoenen=json.dumps(seizoenen), competities=json.dumps(competities))

# hier komt de code voor dynamische drop down
# @app.route('/select_county', methods=['POST'])
# def select_reeks():
#    reeks = ''
#    for entry in ...your_database_query...:
#        reeks += '<option value="{}">{}</option>'.format(entry)
#    return reeks


@app.route('/gebruiker_aanmaken', methods=['GET', 'POST'])
@login_admin_required
def registreer():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Gebruiker(gebruikersnaam=form.username.data, naam=form.name.data)
        user.set_password(form.password.data)
        user.rechten = form.rechten.data
        db.session.add(user)
        db.session.commit()
        flash('Nieuwe gebruiker geregistreerd')
        return redirect(url_for('index'))
    return render_template('registratieformulier.html', title='Registratie Formulier', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        gebruiker = Gebruiker.query.filter_by(gebruikersnaam=form.username.data).first()
        if gebruiker is None or not gebruiker.check_password(form.password.data):
            flash('Verkeerde gebruikersnaam of paswoord')
            return redirect(url_for('login'))
        login_user(gebruiker, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log in', form=form)


# log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# over pagina met info over app
@app.route('/over')
def over():
    return render_template('over.html')