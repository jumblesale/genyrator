Feature: performing operations on a simple schema

  Background:
    Given I have an entity "BookStore" with properties
    | name         | type     | nullable |
    | book_name    | str      | False    |
    | publish_date | date     | False    |
    | in_stock     | int      | False    |
    | rating       | float    | True     |
    And identifier column "book_id" with type "int"
    And I create a schema "books" from those entities
    And the app is running
    And I have json data
    """
    {
      "id": 3,
      "bookName": "the dispossessed",
      "publishDate": "1974-05-21",
      "inStock": 3,
      "rating": 11.6
    }
    """

  Scenario: requesting a non-existing entity
     When I make a "GET" request to "/book-store/1"
     Then I get http status "404"

  Scenario: creating a new entity with correct data
     When I make a "PUT" request to "/book-store/3" with that json data
     Then I get http status "201"
      And I can get entity "/book-store/3"

  Scenario: creating an entity with non-dict data
    Given I have text data
    """{
      "snake"="🐍
    """
    When I make a "PUT" request to "/book-store/3" with that json data
    Then I get http status "400"

  Scenario: creating an entity with incorrect data
    Given I have json data
    """
    {
      "id": 3,
      "bookName": 3,
      "publishDate": "hello",
      "inStock": null,
      "rating": "5"
    }
    """
    When I make a "PUT" request to "/book-store/3" with that json data
    Then I get http status "400"

  Scenario: creating a new entity with null values
    Given I have json data
    """
    {
      "id": 3,
      "bookName": "the dispossessed",
      "publishDate": "1974-05-21",
      "inStock": 3,
      "rating": null
    }
    """
    When I make a "PUT" request to "/book-store/3" with that json data
    Then I get http status "201"
     And I can get entity "/book-store/3"
     And that response matches the original data

  Scenario: updating an existing entity
    Given I make a "PUT" request to "/book-store/3" with that json data
      And I have json data
      """
      {
        "id": 3,
        "bookName": "the disposssesssed",
        "publishDate": "1974-05-22",
        "inStock": 2,
        "rating": 12.4
      }
      """
     When I make a "PUT" request to "/book-store/3" with that json data
     Then I get http status "201"
      And I can get entity "/book-store/3"
      And that response matches the original data

  Scenario: deleting an entity
    Given I make a "PUT" request to "/book-store/3" with that json data
     When I make a "DELETE" request to "/book-store/3"
     Then I get http status "204"
      And I cannot get entity "/book-store/3"

  Scenario: patching an entity
    Given I make a "PUT" request to "/book-store/3" with that json data
      And I have json data
      """
      {
        "bookName": "the disposssesssed"
      }
      """
    When I make a "PATCH" request to "/book-store/3" with that json data
    Then I get http status "200"
     And I can get entity "/book-store/3"
     And the response has "bookName" with value "the disposssesssed"
