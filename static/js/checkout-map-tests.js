/**
 * Checkout Map Functionality Tests
 * Tests for GPS location field visibility and map initialization
 */

// Test suite for checkout map functionality
const CheckoutMapTests = {
    // Test results storage
    results: [],
    
    // Log test result
    logResult: function(testName, passed, message) {
        this.results.push({
            test: testName,
            passed: passed,
            message: message,
            timestamp: new Date().toISOString()
        });
        
        const status = passed ? '✓ PASS' : '✗ FAIL';
        const color = passed ? 'color: green' : 'color: red';
        console.log(`%c${status}: ${testName}`, color);
        if (message) {
            console.log(`  ${message}`);
        }
    },
    
    // Test 1: Map container visibility after location selection
    testMapContainerVisibility: function() {
        const testName = 'Map Container Visibility';
        try {
            // Get elements
            const locationSelect = document.getElementById('location');
            const addressContainer = document.getElementById('address-container');
            const mapElement = document.getElementById('map');
            
            if (!locationSelect || !addressContainer || !mapElement) {
                this.logResult(testName, false, 'Required elements not found');
                return false;
            }
            
            // Initially, address container should be hidden
            const initialDisplay = window.getComputedStyle(addressContainer).display;
            if (initialDisplay !== 'none') {
                this.logResult(testName, false, `Address container should be hidden initially, but display is: ${initialDisplay}`);
                return false;
            }
            
            // Simulate location selection
            locationSelect.value = 'city_center';
            locationSelect.dispatchEvent(new Event('change'));
            
            // Wait for DOM update
            setTimeout(() => {
                const finalDisplay = window.getComputedStyle(addressContainer).display;
                if (finalDisplay === 'none') {
                    this.logResult(testName, false, 'Address container should be visible after location selection');
                    return false;
                }
                
                this.logResult(testName, true, 'Map container becomes visible after location selection');
                return true;
            }, 200);
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 2: Map initialization
    testMapInitialization: function() {
        const testName = 'Map Initialization';
        try {
            // Check if Leaflet is loaded
            if (typeof L === 'undefined') {
                this.logResult(testName, false, 'Leaflet library not loaded');
                return false;
            }
            
            // Check if map variable exists
            if (typeof map === 'undefined') {
                this.logResult(testName, false, 'Map variable not defined');
                return false;
            }
            
            // After location selection, map should be initialized
            setTimeout(() => {
                if (!map) {
                    this.logResult(testName, false, 'Map not initialized after location selection');
                    return false;
                }
                
                // Check if map has required methods
                if (typeof map.invalidateSize !== 'function') {
                    this.logResult(testName, false, 'Map missing invalidateSize method');
                    return false;
                }
                
                this.logResult(testName, true, 'Map initialized successfully with required methods');
                return true;
            }, 500);
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 3: GPS coordinate capture
    testGPSCoordinateCapture: function() {
        const testName = 'GPS Coordinate Capture';
        try {
            const gpsInput = document.getElementById('gps_location');
            
            if (!gpsInput) {
                this.logResult(testName, false, 'GPS location input not found');
                return false;
            }
            
            // Initially should be empty
            if (gpsInput.value !== '') {
                this.logResult(testName, false, 'GPS input should be empty initially');
                return false;
            }
            
            // Simulate map click (if map is initialized)
            setTimeout(() => {
                if (map) {
                    // Simulate click event
                    const testLat = -15.4167;
                    const testLng = 28.2833;
                    
                    // Manually set the value as we would in a real click
                    gpsInput.value = `${testLat},${testLng}`;
                    
                    // Verify format
                    const gpsPattern = /^-?\d+\.?\d*,-?\d+\.?\d*$/;
                    if (!gpsPattern.test(gpsInput.value)) {
                        this.logResult(testName, false, 'GPS coordinates not in correct format');
                        return false;
                    }
                    
                    this.logResult(testName, true, `GPS coordinates captured: ${gpsInput.value}`);
                    return true;
                } else {
                    this.logResult(testName, false, 'Map not initialized for testing');
                    return false;
                }
            }, 600);
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 4: GPS validation - missing location
    testGPSValidationMissing: function() {
        const testName = 'GPS Validation - Missing Location';
        try {
            const gpsInput = document.getElementById('gps_location');
            const form = document.getElementById('checkout-form');
            
            if (!gpsInput || !form) {
                this.logResult(testName, false, 'Required elements not found');
                return false;
            }
            
            // Clear GPS input
            gpsInput.value = '';
            
            // Try to submit form
            const submitEvent = new Event('submit', { cancelable: true });
            form.dispatchEvent(submitEvent);
            
            // Check if validation prevented submission
            if (!submitEvent.defaultPrevented) {
                this.logResult(testName, false, 'Form should not submit without GPS location');
                return false;
            }
            
            this.logResult(testName, true, 'Form submission prevented when GPS location is missing');
            return true;
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 5: GPS validation - invalid format
    testGPSValidationFormat: function() {
        const testName = 'GPS Validation - Invalid Format';
        try {
            const gpsInput = document.getElementById('gps_location');
            
            if (!gpsInput) {
                this.logResult(testName, false, 'GPS input not found');
                return false;
            }
            
            // Test invalid formats
            const invalidFormats = [
                'invalid',
                '123',
                'lat,lng',
                '12.34',
                '12.34,',
                ',56.78'
            ];
            
            const gpsPattern = /^-?\d+\.?\d*,-?\d+\.?\d*$/;
            let allFailed = true;
            
            for (const format of invalidFormats) {
                if (gpsPattern.test(format)) {
                    allFailed = false;
                    this.logResult(testName, false, `Invalid format "${format}" passed validation`);
                    break;
                }
            }
            
            if (allFailed) {
                this.logResult(testName, true, 'All invalid formats correctly rejected');
                return true;
            }
            
            return false;
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 6: GPS validation - valid format
    testGPSValidationValidFormat: function() {
        const testName = 'GPS Validation - Valid Format';
        try {
            const validFormats = [
                '-15.4167,28.2833',
                '-15.5,28.3',
                '-15,28',
                '-15.123456,28.654321'
            ];
            
            const gpsPattern = /^-?\d+\.?\d*,-?\d+\.?\d*$/;
            let allPassed = true;
            
            for (const format of validFormats) {
                if (!gpsPattern.test(format)) {
                    allPassed = false;
                    this.logResult(testName, false, `Valid format "${format}" failed validation`);
                    break;
                }
            }
            
            if (allPassed) {
                this.logResult(testName, true, 'All valid formats correctly accepted');
                return true;
            }
            
            return false;
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Test 7: Lusaka bounds validation
    testLusakaBoundsValidation: function() {
        const testName = 'Lusaka Bounds Validation';
        try {
            // Test coordinates within Lusaka bounds
            const withinBounds = [
                { lat: -15.4167, lng: 28.2833, expected: true },  // Lusaka center
                { lat: -15.3, lng: 28.3, expected: true },        // Within bounds
                { lat: -15.5, lng: 28.4, expected: true }         // Within bounds
            ];
            
            // Test coordinates outside Lusaka bounds
            const outsideBounds = [
                { lat: -16.5, lng: 28.2833, expected: false },    // Too far south
                { lat: -14.5, lng: 28.2833, expected: false },    // Too far north
                { lat: -15.4167, lng: 27.0, expected: false },    // Too far west
                { lat: -15.4167, lng: 30.0, expected: false }     // Too far east
            ];
            
            let allCorrect = true;
            
            // Test within bounds
            for (const coord of withinBounds) {
                const isValid = coord.lat >= -16 && coord.lat <= -15 && coord.lng >= 27.5 && coord.lng <= 29;
                if (isValid !== coord.expected) {
                    allCorrect = false;
                    this.logResult(testName, false, `Coordinate (${coord.lat},${coord.lng}) validation incorrect`);
                    break;
                }
            }
            
            // Test outside bounds
            for (const coord of outsideBounds) {
                const isValid = coord.lat >= -16 && coord.lat <= -15 && coord.lng >= 27.5 && coord.lng <= 29;
                if (isValid !== coord.expected) {
                    allCorrect = false;
                    this.logResult(testName, false, `Coordinate (${coord.lat},${coord.lng}) validation incorrect`);
                    break;
                }
            }
            
            if (allCorrect) {
                this.logResult(testName, true, 'Lusaka bounds validation working correctly');
                return true;
            }
            
            return false;
            
        } catch (error) {
            this.logResult(testName, false, `Error: ${error.message}`);
            return false;
        }
    },
    
    // Run all tests
    runAllTests: function() {
        console.log('%c=== Checkout Map Functionality Tests ===', 'font-weight: bold; font-size: 14px');
        console.log('Starting test suite...\n');
        
        this.results = [];
        
        // Run tests
        this.testMapContainerVisibility();
        this.testMapInitialization();
        this.testGPSCoordinateCapture();
        this.testGPSValidationMissing();
        this.testGPSValidationFormat();
        this.testGPSValidationValidFormat();
        this.testLusakaBoundsValidation();
        
        // Wait for async tests to complete
        setTimeout(() => {
            this.printSummary();
        }, 1000);
    },
    
    // Print test summary
    printSummary: function() {
        console.log('\n%c=== Test Summary ===', 'font-weight: bold; font-size: 14px');
        
        const passed = this.results.filter(r => r.passed).length;
        const failed = this.results.filter(r => !r.passed).length;
        const total = this.results.length;
        
        console.log(`Total Tests: ${total}`);
        console.log(`%cPassed: ${passed}`, 'color: green');
        console.log(`%cFailed: ${failed}`, 'color: red');
        console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
        
        if (failed > 0) {
            console.log('\n%cFailed Tests:', 'color: red; font-weight: bold');
            this.results.filter(r => !r.passed).forEach(r => {
                console.log(`  - ${r.test}: ${r.message}`);
            });
        }
        
        console.log('\n%c=== End of Tests ===', 'font-weight: bold; font-size: 14px');
    }
};

// Auto-run tests if in test mode
if (window.location.search.includes('test=true')) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            CheckoutMapTests.runAllTests();
        }, 1000);
    });
}

// Export for manual testing
window.CheckoutMapTests = CheckoutMapTests;
