document.addEventListener("DOMContentLoaded", () => {
    if ($('#fz_key_form').length) {
        FTVLSapiRequest('');

        const apiButton = document.getElementById('fz_key_form_key_bttn');
        apiButton.addEventListener('click', function(event) {
            event.preventDefault();  // Prevents the form from submitting

            var values = {
                'KC_API_KEY': $('#fz_key_form_kc_key').val(),
                'KC_API_SECRET': $('#fz_key_form_kc_secret').val(),
                'KC_API_PASSPHRASE': $('#fz_key_form_kc_passphrase').val()
            }
            FTVLSapiRequest(values);
        });

    }
});

function FTVLSapiRequest(values) {

    $('#fz_key_form_key_bttn').html('Saving...');
    // Get CSRF token from meta tag
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'fz_fetcher');
    formData.append('js_function_sub', 'api');// Append additional data if needed
    Object.keys(values).forEach(key => {
      formData.append(key, values[key]);
    });

console.log(formData);

    fetch(GASAM_fi_zelf_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

console.log(data);

        $('#fz_key_form_key_bttn').html('Save');
        $('#fz_key_form_kc_key').val(data['KC_API_KEY']);
        $('#fz_key_form_kc_secret').val(data['KC_API_SECRET']);
        $('#fz_key_form_kc_passphrase').val(data['KC_API_PASSPHRASE']);

    })
    .catch(error => {
        console.error('Error:', error);
    });

}