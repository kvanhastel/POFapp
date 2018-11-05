from app import db,Config
from app.models import Speler

Speler.query.delete()
db.session.commit()  # database schrijven