// static/js/main.js

// Wait for the DOM to fully load
document.addEventListener('DOMContentLoaded', () => {
    // Get elements
    const toggleBtn = document.getElementById('toggle-btn');
    const profileImg = document.querySelector('.profile-img');

    // Check if elements exist to avoid errors
    if (toggleBtn && profileImg) {
        // Initial state
        let isVisible = true;

        // Add click event listener to the button
        toggleBtn.addEventListener('click', () => {
            if (isVisible) {
                profileImg.style.display = 'none'; // Hide the image
                toggleBtn.textContent = 'Show Image'; // Update button text
            } else {
                profileImg.style.display = 'block'; // Show the image
                toggleBtn.textContent = 'Hide Image'; // Update button text
            }
            isVisible = !isVisible; // Toggle the state
        });
    } else {
        console.error('Button or image not found in the DOM');
    }
});