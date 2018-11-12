from app import app
from flask import render_template, redirect, url_for, flash, request, json, jsonify, g
from app.forms import LoginForm, RegistrationForm, BasisloegenForm, DatabaseForm, TerugbetalingsForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Gebruiker, Speler, Ploeg
from werkzeug.urls import url_parse
from app import db, importeerdata
from functools import wraps
from app import Config
from sqlalchemy import or_, and_, exists
from app.ziekenfonds import maak_document_ziekenfonds
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def login_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rechten != "administrator":
            flash('geen rechten tot deze pagina', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def login_werkgroep_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rechten != "werkgroep" and current_user.rechten != "administrator":
            flash('geen rechten tot deze pagina', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def login_ploegkapitein_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('geen rechten tot deze pagina', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# startpagina route
@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

# route voor ploegopstellingsformulier pagina
@app.route('/ploegopstellingsformulier')
@login_ploegkapitein_required
def ploegopstellingsformulier():
    return render_template('ploegopstellingsformulier.html')

# route voor terugbetalingsformulier ziekenfonds pagina
@app.route('/terugbetaling', methods=['GET','POST'])
def terugbetalingsformulier():
    terugbetaling_form = TerugbetalingsForm()
    if terugbetaling_form.validate_on_submit():

        #selected_speler = Speler.query.filter(and_(Speler.firstname) == terugbetaling_form.speler_voornaam.data.lower(), Speler.lastname) == terugbetaling_form.speler_familienaam.data.lower())).first()
        selected_speler = Speler.query.filter(and_(Speler.firstname.ilike(terugbetaling_form.speler_voornaam.data), Speler.lastname.ilike(terugbetaling_form.speler_familienaam.data))).first()
        if selected_speler is not None:
            maak_document_ziekenfonds(selected_speler, terugbetaling_form.ziekenfonds.data)
        else:
            flash('Je bent geen lid of je hebt je naam verkeerd ingegeven', 'danger')
            return redirect(url_for('terugbetalingsformulier'))
    return render_template('terugbetalingsformulier.html', terugbetaling_form=terugbetaling_form)


# route voor reservespelers pagina
@app.route('/reservespelers')
@login_ploegkapitein_required
def reservespelers():
    return render_template('reservespelers.html')


# route voor spelerslijst pagina
@app.route('/spelerslijst')
@login_ploegkapitein_required
def spelerslijst():
    #spelers = Speler.query.all()
    # filter om alleen competitiespelers te selecteren
    spelers = Speler.query.filter((Speler.role =='Speler') | (Speler.role == 'Uitgeleende speler')).filter(or_(Speler.typename == 'Competitiespeler', Speler.typename == 'Jeugd')).filter(Speler.website == 'http://www.interclub.be').all()
    return render_template('spelerslijst.html', spelers=spelers)

# route voor speler pagina
@app.route('/speler/<string:memberid>/')
@login_ploegkapitein_required
def speler(memberid):
        s = Speler.query.filter_by(memberid=memberid).first()
        return render_template('speler.html', s=s)

# route voor basisploegen pagina
@app.route('/basisploegen')
@login_werkgroep_required
def basisploegen():
    aanmaak_basisploegen_form = BasisloegenForm()
    basisploegen_form = BasisloegenForm()
    return render_template('basisploegen.html', basisploegen_form=basisploegen_form, aanmaak_basisploegen_form=aanmaak_basisploegen_form)

# route voor aanmaak nieuwe basisploeg
@app.route('/aanmaak_basisploeg')
@login_werkgroep_required
def aanmaak_basisploeg():
    aanmaak_basisploegen_form = BasisloegenForm()
    basisploegen_form = BasisloegenForm()
    if aanmaak_basisploegen_form.validate_on_submit():
        flash('Aanmaak basisploeg gelukt', 'success')
        return redirect(url_for('aanmaak_basisploeg'))
    return render_template('basisploegen.html', basisploegen_form=basisploegen_form, aanmaak_basisploegen_form=aanmaak_basisploegen_form)

# hier komt de code voor dynamische drop down
# @app.route('/select_county', methods=['POST'])
# def select_reeks():
#    reeks = ''
#    for entry in ...your_database_query...:
#        reeks += '<option value="{}">{}</option>'.format(entry)
#    return reeks


# administatie pagina en routes

# database update route
@app.route('/database_update', methods=['GET', 'POST'])
@login_admin_required
def database_update():

    database_update_form = DatabaseForm()
    aanmaak_gebruiker_form = RegistrationForm()

    if database_update_form.validate_on_submit():
        importeerdata.importeernaardatabase(app)
        flash('Update database succesvol', 'success')
        return redirect(url_for('database_update'))
    return render_template('administratie.html', title='Administratie', database_update_form=database_update_form, aanmaak_gebruiker_form=aanmaak_gebruiker_form)

# aanmaak gebruiker route
@app.route('/aanmaak_gebruiker', methods=['GET', 'POST'])
@login_admin_required
def aanmaak_gebruiker():
    #TODO: opdelen in verschillende administratieve taken:
    #       - nieuwe gebruikers toevoegen

    database_update_form = DatabaseForm()
    aanmaak_gebruiker_form = RegistrationForm()

    if aanmaak_gebruiker_form.validate_on_submit():
        user = Gebruiker(gebruikersnaam=aanmaak_gebruiker_form.username.data, naam=aanmaak_gebruiker_form.name.data)
        user.set_password(aanmaak_gebruiker_form.password.data)
        user.rechten = aanmaak_gebruiker_form.rechten.data
        db.session.add(user)
        db.session.commit()
        flash('Nieuwe gebruiker aangemaakt', 'success')
        return redirect(url_for('aanmaak_gebruiker'))
    return render_template('administratie.html', title='Administratie', aanmaak_gebruiker_form=aanmaak_gebruiker_form, database_update_form=database_update_form)

    #       - database vernieuwen en wachtwoord opgeven


# route voor login website

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        gebruiker = Gebruiker.query.filter_by(gebruikersnaam=form.username.data).first()
        if gebruiker is None or not gebruiker.check_password(form.password.data):
            flash('Verkeerde gebruikersnaam of paswoord', 'danger')
            return redirect(url_for('login'))
        login_user(gebruiker, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log in', form=form)


# route voor log out website
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# over pagina met info over app
@app.route('/over')
def over():
    return render_template('over.html')