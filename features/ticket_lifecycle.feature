Feature: Ticket lifecycle
  Scenario: Owner cannot buddy their own ticket
    Given I am logged in as tester "owner"
    And I have created a ticket ready for buddy
    When I try to buddy that ticket
    Then I should see "You cannot buddy a ticket that you created."

  Scenario: Another tester can buddy a ticket
    Given I am logged in as tester "owner"
    And I have created a ticket ready for buddy
    And I am logged in as tester "buddy"
    When I buddy that ticket
    Then I should see "Ticket marked as buddied."
