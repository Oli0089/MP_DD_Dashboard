Feature: Comparison dashboard workflow

  Scenario: Authenticated user can access the Comparison page
    Given I am logged in as a tester
    When I open the comparison page
    Then the comparison page is displayed

  Scenario: Authenticated user can access the Results page
    Given I am logged in as a tester
    When I open the results page
    Then the results page is displayed

  Scenario: Comparison result updates an SWH card
    Given I am logged in as a tester
    When a comparison result is stored for "acturis_nb" as "Passed"
    And I open the comparison page
    Then I should see the SWH status "Passed"

  Scenario: Finalise DD Run is unavailable before all SWHs are complete
    Given I am logged in as a tester
    When I open the comparison page
    Then the Finalise DD Run button should be disabled

  Scenario: Results page shows saved DD history
    Given I am logged in as a tester
    And a failed DD run exists
    When I open the results page
    Then I should see the saved DD run history
