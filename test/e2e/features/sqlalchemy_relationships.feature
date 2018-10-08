Feature: SQLAlchemy relationships

  Background:
    Given I have the example "bookshop" application

  Scenario: Following a 1-to-many relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I put a book entity with a relationship to that author
     When I get that "author" SQLAlchemy model
     Then "sql_author.books" should have "2" items in it
  
  Scenario: Following a many-to-1 relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I put a book entity with a relationship to that author
     When I get that "book" SQLAlchemy model
     Then "sql_book.author" should be that author
      And "sql_book.collaborator" should be None

  Scenario: Following other many-to-1 relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I also put a collaborator relationship to that author
     When I get that "book" SQLAlchemy model
     Then "sql_book.author" should be that author
      And "sql_book.collaborator" should be that author
