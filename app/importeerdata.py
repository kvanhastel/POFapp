import csv
from datetime import datetime
from app import db,Config
from app.models import Speler
from requests import sessions
from bs4 import BeautifulSoup

if __name__ == "__main__":

    def data_naar_datum(data):
        if data != '':
            return datetime.strptime(data, '%d-%m-%Y')
    def data_naar_bool(data):
        if data == ('False' or ''):
            return 0
        if data == 'True':
            return 1

    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    login_url = Config.LOGIN_URL
    username = Config.VBL_LOGIN
    password = Config.VBL_PASSWORD

    login_sessie = sessions.Session()
    login_site = login_sessie.get(login_url)
    login_site_data = BeautifulSoup(login_site.content, "lxml")

    VIEWSTATE = login_site_data.find(id="__VIEWSTATE")['value']
    VIEWSTATEGENERATOR = login_site_data.find(id="__VIEWSTATEGENERATOR")['value']
    EVENTVALIDATION = login_site_data.find(id="__EVENTVALIDATION")['value']

    login_data = {"__VIEWSTATE": VIEWSTATE,
                  "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
                  "__EVENTVALIDATION": EVENTVALIDATION,
                  "ctl01$ctl01$container$content$ctl00$cphPage$cphPage$pnlLogin$UserName": username,
                  "ctl01$ctl01$container$content$ctl00$cphPage$cphPage$pnlLogin$Password": password,
                  "ctl01$ctl01$container$content$ctl00$cphPage$cphPage$pnlLogin$LoginButton": "Inloggen"}

    login_site = login_sessie.post(login_url, data=login_data)

    login_site_data = BeautifulSoup(login_site.content, "lxml")
    id = find_between(str(login_site_data), r'group.aspx?id=', r'&amp;gid')
    gid = find_between(str(login_site_data), r'&amp;gid=', r'&amp;p=3')
    xlsx_param = 'glid=0'
    csv_param = 'ft=1'
    leden = 'export_memberperrolepergroup.aspx'
    data_url = "https://badmintonvlaanderen.toernooi.nl/organization/export/" + leden + "?id=" + id + "&gid=" + gid + '&' + csv_param + "&" + xlsx_param
    print(data_url)
    data_site = login_sessie.get(data_url, data=login_data)
    spelersgegevens = [line.decode('utf-8') for line in data_site.iter_lines()]
    # eerste regel weghalen
    spelersgegevens.pop(0)
    #gegevens in csv bestand stoppen
    spelers_bestand = csv.reader(spelersgegevens, delimiter=';')
    # oude gegevens verwijderen
    Speler.query.delete()
    #database vullen met nieuwe gegevens
    for rij in spelers_bestand:
        speler = Speler(
                groupcode=rij[0],
                groupname=rij[1],
                code=rij[2],
                memberid=rij[3],
                lastname=rij[4],
                lastname2=rij[5],
                middlename=rij[6],
                firstname=rij[7],
                address=rij[8],
                address2=rij[9],
                address3=rij[10],
                postalcode=rij[11],
                city=rij[12],
                state=rij[13],
                country=rij[14],
                gender=rij[15],
                dob=data_naar_datum(rij[16]),
                phone=rij[17],
                phone2=rij[18],
                mobile=rij[19],
                fax=rij[20],
                fax2=rij[21],
                email=rij[22],
                website=rij[23],
                categoryname=rij[24],
                startdate=data_naar_datum(rij[25]),
                endate=data_naar_datum(rij[26]),
                role=rij[27],
                playerlevelsingle=rij[28],
                playerleveldouble=rij[29],
                playerlevelmixed=rij[30],
                typename=rij[31],
                geen_badminton_magazine=data_naar_bool(rij[32]),
                handicap=data_naar_bool(rij[33]),
                nieuwsbrief=data_naar_bool(rij[34]),
                partners=data_naar_bool(rij[35]),
                betaald=data_naar_bool(rij[36]),
                betaald_bedrag=rij[37],
                datum_betaling=data_naar_datum(rij[38]),
                email_vader=rij[39],
                email_moeder=rij[40],
                gsm_vader=rij[41],
                gsm_moeder=rij[42],
                kyu=rij[43],
                kyu_gaat_in_op=data_naar_datum(rij[44]),
                verwittiging=data_naar_bool(rij[45]),
                po_id_votas=rij[46]
        )
        db.session.add(speler) #record in database plaatsen

    db.session.commit() #database schrijven