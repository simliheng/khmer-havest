document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdown = document.querySelector('.dropdown');
    
    dropdownToggle.addEventListener('click', function() {
        dropdown.classList.toggle('show');
    });

    // Optional: Close dropdown if clicked outside
    document.addEventListener('click', function(event) {
        if (!dropdown.contains(event.target) && !dropdownToggle.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    });
});
