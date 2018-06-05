Feature: Generating a schema

  Background:
    Given I have an entity with properties
    | name      | type |
    | test_name | str  |
    And identifier column "test_id" with type "int"
    And I create a schema from those entities

  Scenario: generating a schema
    Given I write that schema
     Then I can import the generated app
      And I can run the generated app
