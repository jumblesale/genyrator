Feature: performing operations on a simple schema

  Background:
    Given I have an entity "BookStore" with properties
    | name         | type     | nullable |
    | book_name    | str      | False    |
    | publish_date | date     | False    |
    | in_stock     | int      | False    |
    | rating       | float    | True     |
    And identifier column "book_id" with type "UUID"
    And I create a schema from those entities
    And the app is running

  Scenario: creating a new entity with POST
    Given I have json data
    """
    {
      "bookName": "the dispossessed",
      "publishDate": "1974-05-21",
      "inStock": 3,
      "rating": null
    }
    """
    When I make a "POST" request to "/book-store" with that json data
    Then I get http status "201"
     And that response matches the original data plus "id"
     And I can get entity "/book-store/{id}" using that response data
