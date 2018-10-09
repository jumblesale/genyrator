Feature: SQLAlchemy relationships

  Background:
    Given I have the example "bookshop" application

  Scenario: Following a to-many relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I put a book entity with a relationship to that author
     When I get that "author" SQLAlchemy model
     Then "sql_author.books" should have "2" items in it
  
  Scenario: Following a to-1 relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I put a book entity with a relationship to that author
     When I get that "book" SQLAlchemy model
     Then "sql_book.author" should be that author
      And "sql_book.collaborator" should be None

  Scenario: Following other to-1 relationship
    Given I put an example "author" entity
      And I put a book entity with a relationship to that author
      And I also put a collaborator relationship to that author
     When I get that "book" SQLAlchemy model
     Then "sql_book.author" should be that author
      And "sql_book.collaborator" should be that author

  Scenario: Following self referencing to-1 relationship
    Given I put an example "author" entity called "author1"
      And I put an example "author" entity called "author2" with a "favouriteAuthorId" from "author1"
     When I get the "author" called "author2" SQLAlchemy model
     Then "sql_author.favourite_author" should be "author1"
      And "sql_author.hated_author" should be None

  Scenario: Following a self referencing to-many relationship
    Given I put an example "author" entity called "author1"
      And I put an example "author" entity called "author2" with a "favouriteAuthorId" from "author1"
      And I put an example "author" entity called "author3" with a "favouriteAuthorId" from "author1"
      When I get the "author" called "author1" SQLAlchemy model
      Then "sql_author.favourite_author" should be None
       And "sql_author.favourite_of" should have "2" items in it
