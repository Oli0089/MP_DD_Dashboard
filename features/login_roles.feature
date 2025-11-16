Feature: Login and role access
  Scenario: Invalid login shows an error
    Given the app is initialised
    When I submit the login form with username "wronguser" and password "wrongpass"
    Then I should see "Invalid username or password."
