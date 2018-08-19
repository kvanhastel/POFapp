import os
from datetime import datetime
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # sleutel om verschillende zaken te beveiligen en encrypteren
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Bct13lt'

    # database info
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # info voor inloggen op website VBL
    VBL_LOGIN = 'VanhastelS2N'
    VBL_PASSWORD = 'Bct13lt'
    LOGIN_URL = 'https://badmintonvlaanderen.toernooi.nl/member/login.aspx'

    # lijst selecteerbare seizoenen
    year = datetime.today().year%100
    # lijst seizoenen. Vorig seizoen, huidig seizoen en volgend seizoen
    SEIZOENEN = [('1',str(year-2) + '-' + str(year-1)), ('2',str(year-1) + '-' + str(year)), ('3',str(year) + '-' + str(year+1))]

    #lijst competities
    COMPETITIES = [('1','Dames'),('2','Heren'),('3','Gemengd'),('4','Veteranen')]

    # lijst klassementen
    KLASSEMENTEN = {
                    'A': 20,
                    'B1': 10,
                    'B2': 6,
                    'C1': 4,
                    'C2': 2,
                    'D': 1
                    }

    # lijst afdelingen
    AFDELINGEN = [
        '1e liga',
        '2e liga A',
        '2e liga B',
        '3e liga A',
        '3e liga B',
        '3e liga C',
        '3e liga D',
        '1e provinciale',
        '2e provinciale A',
        '2e provinciale B',
        '3e provinciale A',
        '3e provinciale B',
        '3e provinciale C',
        '4e provinciale A',
        '4e provinciale B',
        '4e provinciale C',
        '5e provinciale A',
        '5e provinciale B',
        '5e provinciale C'
    ]
