document.addEventListener("DOMContentLoaded", () => {
    if ($('#typing_speed_test_key_form_key').length) {
        TSTapiRequest('');

        const apiButton = document.getElementById('typing_speed_test_key_form_key_bttn');
        apiButton.addEventListener('click', function(event) {
            event.preventDefault();  // Prevents the form from submitting
            TSTapiRequest($('#typing_speed_test_key_form_key').val());
        });

    }
});

function TSTapiRequest(api_val) {

    // Get CSRF token from meta tag
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'typing_speed_test_api'); // Append additional data if needed
    formData.append('api_val', api_val); // Append additional data if needed

    fetch(GASAM_typing_speed_test_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        $('#typing_speed_test_key_form_key').val(data['key']);

    })
    .catch(error => {
        console.error('Error:', error);
    });

}