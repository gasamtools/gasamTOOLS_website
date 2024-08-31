document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('app_management_add_new_app_form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent any default behavior

            // Get CSRF token from meta tag
            var csrfToken = $('meta[name="csrf-token"]').attr('content');


            const formData = new FormData(this);
            const formObject = {'js_function': 'app_management_add_new_app'};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });

            fetch(GASAM_app_management_add_new_app_URL, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
                },
                body: JSON.stringify(formObject)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                form.reset();
                const toastBodyElement = document.getElementById('app_management_add_new_app_toast_body');
                toastBodyElement.innerHTML = "App '"+ data['title'] +"' is registered.";
                var toastElement = new bootstrap.Toast(document.getElementById('app_management_add_new_app_toast'));
                toastElement.show();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
