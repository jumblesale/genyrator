from flask_restplus import Api
from bookshop.resources.Book import api as books_api
from bookshop.resources.Author import api as authors_api
from bookshop.resources.Review import api as reviews_api
from bookshop.resources.Genre import api as genres_api
from bookshop.resources.BookGenre import api as book_genres_api


api = Api(
    title='bookshop',
    version='1.0',
    description='',
)

api.add_namespace(books_api)
api.add_namespace(authors_api)
api.add_namespace(reviews_api)
api.add_namespace(genres_api)
api.add_namespace(book_genres_api)
