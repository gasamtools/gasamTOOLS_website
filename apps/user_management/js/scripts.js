document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('myForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting the traditional way
        const formData = new FormData(this);
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });

console.log(formObject)

        fetch(GASAM_apps_app_management_scripts_URL, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json' // Ensure the server knows to expect JSON
            },
            body: JSON.stringify(formObject)
        }).then(response => {
            return response.json();
        }).then(data => {
            console.log(data); // Handle the response from the server
        }).catch(error => {
            console.error('Error:', error);
        });
    });
});