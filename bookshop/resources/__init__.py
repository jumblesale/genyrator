from flask_restplus import Api
from bookshop.resources.Book import api as books_api
from bookshop.resources.Author import api as authors_api


api = Api(
    title='bookshop',
    version='1.0',
    description='',
)

api.add_namespace(books_api)
api.add_namespace(authors_api)

