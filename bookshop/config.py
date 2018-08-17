from flask import Flask


def config():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookshop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app
