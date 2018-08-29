Feature: Posting new entities with foreign keys

  Background:
    Given I have the example "bookshop" application

  Scenario: Putting a join entity
    Given I put an example "book" entity
      And I put an example "genre" entity
     When I put a "book_genre" join entity
     Then I can see that genre in the response from "book/{id}/genres"

  Scenario: Putting a join entity where the join does not exist
    Given I put an incorrect "book_genre" join entity
     Then I get http status 400

#  Scenario: PATCHing a relationship
#    Given I put an example "book" entity
#      And I put an example "author" entity
#     When I patch that "book" entity with that "author" id
#     Then I can see that book in the response from "author/{id}/books"
