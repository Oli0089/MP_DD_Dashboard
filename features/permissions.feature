Feature: Permissions
  Scenario: Unauthenticated user cannot access admin page
    Given the app is initialised
    When I visit the admin page
    Then I should be redirected to the login page

  Scenario: Non-admin user cannot access admin page
    Given a user exists with username "normaluser" and password "Password1"
    And I log in with username "normaluser" and password "Password1"
    When I visit the admin page
    Then I should be redirected to the home page

  Scenario: Admin user can access admin page
    Given an admin user exists with username "adminuser" and password "Password1"
    And I log in with username "adminuser" and password "Password1"
    When I visit the admin page
    Then I should see "Admin Panel"
