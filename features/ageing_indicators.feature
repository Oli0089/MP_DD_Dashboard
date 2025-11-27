Feature: Ageing indicators
  Scenario: A ticket older than 4 days shows the red indicator
    Given a ticket exists that was created 5 days ago
    When I view the ticket board
    Then I should see the "danger" indicator
