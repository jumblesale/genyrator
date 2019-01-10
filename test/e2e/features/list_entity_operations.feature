Feature: Listing and filtering entities

  Background:
    Given I have the example "bookshop" application
    And I put an example set of books

  Scenario: Filtering by name
    When I list "book" filtered by "name=Peter Rabbit"
    Then I have "1" results


  Scenario: Filtering by rating
    When I list "book" filtered by "rating=3.2"
    Then I have "2" results
