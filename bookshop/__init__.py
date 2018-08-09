from flask_marshmallow import Marshmallow
from bookshop.resources import api
from bookshop.config import config
from bookshop.sqlalchemy import db

app = config()
db.init_app(app)
ma = Marshmallow(app)
api.init_app(app)
