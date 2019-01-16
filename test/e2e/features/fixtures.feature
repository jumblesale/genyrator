Feature: Creating fixtures from SQLAlchemy models

  Scenario: Creating a fixture with all default columns
    Given I have an entity "Book" with properties
      | name   | type  |
      | title  | str   |
      | rating | float |
      And identifier column "book_id" with type "UUID"
      And I create a schema from those entities
      And I write that schema
      And I import the generated app
      And I initialize the database
     When I create a fixture for the "Book" entity
     Then the db contains "1" "Book" entity

  Scenario: Creating a fixture with all the types
    Given I have an entity "Book" with properties
      | name      | type     |
      | title     | str      |
      | rating    | float    |
      | published | date     |
      | created   | datetime |
      | count     | int      |
      | in_stock  | bool     |
      And identifier column "book_id" with type "UUID"
      And I create a schema from those entities
      And I write that schema
      And I import the generated app
      And I initialize the database
     When I create a fixture for the "Book" entity
     Then the db contains "1" "Book" entity
