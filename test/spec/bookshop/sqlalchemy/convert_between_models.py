from expects import expect, be_a
from mamba import description, it

from bookshop.sqlalchemy.convert_between_models import convert_sqlalchemy_model_to_domain_model
from bookshop.sqlalchemy.model import Book
from bookshop.domain.types import DomainModel

with description('converts sqlalchemy models to domain models') as self:
    with it('converts book sqlalchemy model to book domain model'):
        book_sqlalchemy_model = Book()
        expect(
            convert_sqlalchemy_model_to_domain_model(
                book_sqlalchemy_model
            )
        ).to(be_a(DomainModel))
