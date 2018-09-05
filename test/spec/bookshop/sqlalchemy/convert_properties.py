import datetime
import uuid

from mamba import description, it
from sqlalchemy.orm import joinedload

from bookshop.sqlalchemy.convert_properties import convert_sqlalchemy_properties_to_dict_properties
from bookshop.domain.Genre import genre as genre_domain_model
from bookshop.sqlalchemy.model import Genre

BOOK_UUID =  uuid.uuid4()

datetime_now = datetime.datetime.now()
date_now =     datetime.datetime.today()

genre_model = Genre(
    id=1, genre_id=uuid.uuid4(), title='genre',
)

with description('convert_properties') as self:
    with it('converts genreId to id'):
        converted = convert_sqlalchemy_properties_to_dict_properties(
            domain_model=genre_domain_model,
            sqlalchemy_model=genre_model,
            data={

            }
        )
