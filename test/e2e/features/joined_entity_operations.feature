Feature: Posting new entities with foreign keys

  Background:
    Given I have the example "bookshop" application

  Scenario: PUTting a join entity
    Given I put an example "book" entity
      And I put an example "genre" entity
     When I put a "book_genre" join entity
     Then I can see that genre in the response from "book/{id}/genres"
