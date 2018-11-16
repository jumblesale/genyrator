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

  Scenario: Following a self referencing many-to-many relationship
    Given I put an example "book" entity called "myFirstBook"
      And I put an example "book" entity called "mySecondBook"
      And I put an example "book" entity called "myThirdBook"
      And I put an example "related-book" entity called "join1" joining "myFirstBook" to "mySecondBook"
      And I put an example "related-book" entity called "join2" joining "myFirstBook" to "myThirdBook"
      When I get the "book" called "myFirstBook" SQLAlchemy model
      Then "sql_book.related_books" should have "2" items in it
      When I get the "book" called "myThirdBook" SQLAlchemy model
      Then "sql_book.related_books" should have "0" items in it
