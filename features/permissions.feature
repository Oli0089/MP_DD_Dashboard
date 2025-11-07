Feature: Permissions
  Scenario: Unauthenticated user cannot access admin page
    Given the app is initialised
    When I visit the admin page
    Then I should be redirected to the login page
