# Checkout Map Functionality Tests

## Overview

This test suite validates the GPS location field visibility and map initialization functionality in the checkout form.

## Test Coverage

The test suite includes 7 tests covering:

1. **Map Container Visibility** - Verifies that the map container becomes visible after selecting a delivery area
2. **Map Initialization** - Checks that the Leaflet map initializes correctly with required methods
3. **GPS Coordinate Capture** - Tests that clicking on the map captures GPS coordinates
4. **GPS Validation - Missing Location** - Ensures form submission is prevented without GPS coordinates
5. **GPS Validation - Invalid Format** - Validates that invalid coordinate formats are rejected
6. **GPS Validation - Valid Format** - Confirms that valid coordinate formats are accepted
7. **Lusaka Bounds Validation** - Tests geographic bounds checking for Lusaka area

## Running the Tests

### Method 1: Auto-run on Page Load

Add `?test=true` to the checkout URL:

```
http://localhost:8000/checkout/?test=true
```

The tests will automatically run 1 second after page load, and results will be displayed in the browser console.

### Method 2: Manual Execution

1. Open the checkout page in your browser
2. Open the browser's Developer Tools (F12)
3. Go to the Console tab
4. Run the following command:

```javascript
CheckoutMapTests.runAllTests();
```

### Method 3: Individual Test Execution

You can run individual tests by calling them directly:

```javascript
// Run a specific test
CheckoutMapTests.testMapContainerVisibility();
CheckoutMapTests.testGPSValidationFormat();

// View results
console.table(CheckoutMapTests.results);
```

## Test Results

Test results are logged to the console with:
- ✓ PASS (green) for successful tests
- ✗ FAIL (red) for failed tests

A summary is displayed at the end showing:
- Total number of tests
- Number of passed tests
- Number of failed tests
- Success rate percentage
- Details of any failed tests

## Integration with Checkout Page

To include the tests in your checkout page, add this script tag before the closing `</body>` tag:

```html
<script src="{% static 'js/checkout-map-tests.js' %}"></script>
```

## Expected Results

All 7 tests should pass when:
- The checkout page loads correctly
- Leaflet.js library is loaded
- The map container is properly configured
- GPS validation logic is implemented correctly
- Lusaka bounds checking is accurate

## Troubleshooting

### Tests Not Running

- Ensure the script is loaded after the checkout form HTML
- Check that Leaflet.js is loaded before the test script
- Verify that all required element IDs exist in the HTML

### Map Initialization Fails

- Check browser console for Leaflet errors
- Verify internet connection (for loading map tiles)
- Ensure the map container has proper dimensions

### GPS Validation Fails

- Check that the validation regex patterns match the implementation
- Verify that the Lusaka bounds coordinates are correct
- Ensure the form submission handler is properly attached

## Continuous Integration

These tests can be integrated into your CI/CD pipeline using headless browser testing tools like:
- Selenium
- Puppeteer
- Playwright

Example Puppeteer test:

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Navigate to checkout page with test mode
  await page.goto('http://localhost:8000/checkout/?test=true');
  
  // Wait for tests to complete
  await page.waitForTimeout(2000);
  
  // Get test results from console
  const results = await page.evaluate(() => {
    return CheckoutMapTests.results;
  });
  
  // Check if all tests passed
  const allPassed = results.every(r => r.passed);
  
  console.log('Test Results:', results);
  console.log('All Tests Passed:', allPassed);
  
  await browser.close();
  
  process.exit(allPassed ? 0 : 1);
})();
```

## Contributing

When adding new map functionality, please:
1. Add corresponding tests to `checkout-map-tests.js`
2. Update this README with the new test descriptions
3. Ensure all tests pass before committing changes
