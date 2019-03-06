Feature: Custom SQLAlchemy column options

  Background:
    Given I have the example "bookshop" application

  Scenario: Column defaults are correctly applied
    Given I put an example "book" entity
     When I get that "book" SQLAlchemy model
     Then "sql_book.created" should be a recent timestamp
      And "sql_book.updated" should be a recent timestamp

  Scenario: Column onupdate rules are correctly applied
    Given I put an example "book" entity
     When I get that "book" SQLAlchemy model
      And I save the value of "sql_book.updated" as "original_updated"
      And I patch that "book" entity to set "name" to "cave"
      And I get that "book" SQLAlchemy model
     Then "sql_book.updated" should not equal saved value "original_updated"

