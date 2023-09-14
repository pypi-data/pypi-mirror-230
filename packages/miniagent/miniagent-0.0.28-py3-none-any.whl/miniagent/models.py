import enum
from . import db

class YesNoEnum(enum.Enum):
   YES = "YES"
   NO  = "NO"
   
class MaProperties(db.Model):
   id = db.Column(db.Integer, primary_key = True, nullable=False)
   item = db.Column(db.String(100), nullable=False)
   value = db.Column(db.String(500))