from app import app, db
from app.models import Gebruiker, Speler, Ploeg

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Gebruiker':Gebruiker, 'Speler':Speler, 'Ploeg':Ploeg}