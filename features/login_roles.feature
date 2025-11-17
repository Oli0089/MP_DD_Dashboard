Feature: Login and role access

  Scenario: Invalid login shows an error
    Given the app is initialised
    When I submit the login form with username "wronguser" and password "wrongpass"
    Then I should see "Invalid username or password."

  Scenario: Successful login with valid credentials
    Given a user exists with username "testuser" and password "Password1"
    When I log in with username "testuser" and password "Password1"
    Then I should see "Buddy Ticket Tracker"
