function dark() {
    // Get the dark mode switch element by its ID
    var isDarkModeEnabled, darkSwitch = document.getElementById("darkSwitch");
    // Check if the dark mode switch exists in the DOM
    if (darkSwitch) {
        // Determine if dark mode was previously enabled by checking localStorage
        isDarkModeEnabled = localStorage.getItem("theme") === "dark";
        // Set the checkbox state based on whether dark mode was previously enabled
        darkSwitch.checked = isDarkModeEnabled;
        // Apply or remove the "dark" theme based on the checkbox state
        if (isDarkModeEnabled) {
            document.body.setAttribute("data-theme", "dark");
        } else {
            document.body.removeAttribute("data-theme");
        }
        // Add an event listener to the switch for handling user changes
        darkSwitch.addEventListener("click", function () {
            if (document.body.getAttribute("data-theme") === "dark") {
                // If the switch is unchecked, disable dark mode
                document.body.removeAttribute("data-theme");
                localStorage.removeItem("theme"); // Remove the preference from localStorage
            } else {
                // If the switch is checked, enable dark mode
                document.body.setAttribute("data-theme", "dark");
                localStorage.setItem("theme", "dark"); // Save the preference in localStorage
            }
        });
    }
}
dark();