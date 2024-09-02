document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('morse_code_generator_form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent any default behavior

            // Get CSRF token from meta tag
            var csrfToken = $('meta[name="csrf-token"]').attr('content');


            const formData = new FormData(this);
            const formObject = {'js_function': 'morse_code_generator'};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });

            fetch(GASAM_morse_code_generator_URL, {
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
                //form.reset();
                $('#morse_code_generator_div_response').html(data['user_apps_html']);
                $('#morse_code_generator_div_response').show();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
