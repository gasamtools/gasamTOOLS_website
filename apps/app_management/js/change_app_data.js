document.addEventListener("DOMContentLoaded", () => {

    var forms = document.getElementsByClassName('gasam app_management change_app_data form');

    for (var i = 0; i < forms.length; i++) {
        forms[i].addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting the traditional way

            // Get CSRF token from meta tag
            var csrfToken = $('meta[name="csrf-token"]').attr('content');

            const formData = new FormData(this);
            const formObject = {'js_function': 'app_management_change_app_data'};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });

            var form = this; // 'this' refers to the form that triggered the event
            var classList = form.classList; // Get the classList of the form
            var target = classList[classList.length - 2];
            var app = classList[classList.length - 1];

            var button = $('button.app_management.change_app_data.' + target + '.' + app);
            var buttonHTML = button.html();
            button.addClass('btn-loading').attr('disabled', true);
            button.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');

            // Perform fetch with the specified buttonHTML
            performFetch(buttonHTML, csrfToken, formObject, button, app);
        });
    }

    // Define the performFetch function
    function performFetch(buttonHTML, csrfToken, formObject, button, app) {
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
console.log(data)
            button.removeClass('btn-loading').attr('disabled', false);
            if (data['target'] == 'delete_app') {
                $('tr.gasam.app_management.' + app).remove();
            } else {
                button.html(buttonHTML);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

});
