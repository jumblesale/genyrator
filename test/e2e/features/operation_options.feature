Feature: restricting endpoints with operation options

  Scenario: only allowing fetching a single entity
    Given I have operation options "get_one"
      And I create an example app
     When I make a "GET" request to "/example-entity/3"
     Then I get http status "200"
      And making "DELETE,PUT" requests to "/example-entity/3" gives http status "405"
      And making "DELETE,POST" requests to "/example-entities" gives http status "404"

  Scenario: only allowing fetching all of a single entity
    Given I have operation options "get_all"
      And I create an example app
     When I make a "GET" request to "/example-entities"
     Then I get http status "200"
      And making "DELETE,PUT,GET" requests to "/example-entity/3" gives http status "404"
      And making "DELETE,POST" requests to "/example-entities" gives http status "405"

  Scenario: only allowing creating an entity with id
    Given I have operation options "create_with_id"
      And I create an example app
      And I have json data
      """
      {
        "testName": "test"
      }
      """
     When I make a "PUT" request to "/example-entity/3" with that json data
     Then I get http status "201"
      And making "DELETE,GET" requests to "/example-entity/3" gives http status "405"
      And making "DELETE,POST,GET" requests to "/example-entities" gives http status "404"
