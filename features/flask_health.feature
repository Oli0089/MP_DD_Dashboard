Feature: Flask health endpoint
  Scenario: App returns healthy status
    Given the app is initialised
    When I GET "/health"
    Then I receive 200 and JSON status "healthy"