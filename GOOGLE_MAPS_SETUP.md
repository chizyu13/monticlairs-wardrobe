# Google Maps Integration Setup

## Overview
The checkout page now uses Google Maps API with the following features:
- **Address Autocomplete**: Users can type their address and select from suggestions
- **Interactive Map**: Click anywhere on the map to mark delivery location
- **Automatic Pin Placement**: When an address is selected, a pin automatically appears on the map
- **Reverse Geocoding**: Clicking the map automatically fills in the address field
- **Custom Styling**: Dark theme matching your website design

## Setup Instructions

### 1. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Maps JavaScript API**
   - **Places API**
   - **Geocoding API**
4. Go to "Credentials" and create an API key
5. (Optional but recommended) Restrict your API key:
   - Set HTTP referrer restrictions to your domain
   - Restrict API key to only the APIs listed above

### 2. Add API Key to Your Project

Open `templates/home/checkout.html` and replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual API key:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY_HERE&libraries=places&callback=initMap" async defer></script>
```

**Example:**
```html
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&libraries=places&callback=initMap" async defer></script>
```

### 3. Security Best Practices

For production, consider storing the API key in environment variables:

1. Add to your `.env` file:
```
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

2. Update your Django settings (`settings.py`):
```python
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
```

3. Pass it to the template context in your view:
```python
def checkout(request):
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        # ... other context
    }
    return render(request, 'home/checkout.html', context)
```

4. Update the template to use the context variable:
```html
<script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=places&callback=initMap" async defer></script>
```

## Features Implemented

### 1. Address Autocomplete
- Users start typing their address in the "Street Address" field
- Google suggests addresses in Zambia (restricted to 'zm' country code)
- Selecting an address automatically:
  - Places a pin on the map
  - Centers the map on that location
  - Saves GPS coordinates

### 2. Interactive Map
- Users can click anywhere on the map to mark their exact location
- Clicking the map:
  - Places a custom gold pin at that location
  - Automatically fills the address field (reverse geocoding)
  - Saves GPS coordinates

### 3. Visual Feedback
- Map has a dark theme matching your website
- Custom gold marker for delivery location
- Status messages show when location is selected
- Validation ensures GPS location is selected before checkout

### 4. Mobile Responsive
- Map adjusts height on mobile devices (300px)
- Touch-friendly interface
- Autocomplete dropdown works on mobile

## Testing

1. Select a delivery area from the dropdown
2. The map will appear
3. Try typing an address (e.g., "Cairo Road, Lusaka")
4. Select from the suggestions - the pin should appear automatically
5. Try clicking directly on the map - the address field should update
6. Submit the form - GPS coordinates are saved with the order

## Troubleshooting

### Map not loading
- Check browser console for errors
- Verify API key is correct
- Ensure all required APIs are enabled in Google Cloud Console
- Check for billing issues (Google Maps requires billing to be enabled)

### Autocomplete not working
- Ensure Places API is enabled
- Check that `libraries=places` is in the script URL
- Verify country restriction is set to 'zm'

### Coordinates not saving
- Check that the hidden input `gps_location` is being populated
- Look for JavaScript errors in the console
- Ensure form validation is passing

## Cost Considerations

Google Maps API has a free tier:
- $200 free credit per month
- Maps JavaScript API: $7 per 1,000 loads
- Places Autocomplete: $2.83 per 1,000 requests
- Geocoding API: $5 per 1,000 requests

For a small e-commerce site, you'll likely stay within the free tier.

## Alternative: Environment-Based Configuration

If you want to use different API keys for development and production, update your view:

```python
# views.py
from django.conf import settings

def checkout(request):
    # ... your existing code ...
    
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'base_price': base_price,
        'total_price': total_price,
        # ... other context
    }
    return render(request, 'home/checkout.html', context)
```

Then in the template, use:
```html
<script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=places&callback=initMap" async defer></script>
```
