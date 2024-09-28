document.addEventListener("DOMContentLoaded", () => {

    const modalLoadingElement = document.getElementById('typing_speed_testLoadingModal');
    const this_modal = bootstrap.Modal.getOrCreateInstance(modalLoadingElement, {
        backdrop: 'static',
        keyboard: false // Set to true if you want to allow closing via the keyboard
    });
        if (this_modal) {
            this_modal.show();
            $('.modal-backdrop.fade.show').show();
        } else {
            console.error('Modal instance not found.');
        }

    // Get CSRF token from meta tag
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'typing_speed_test_ini'); // Append additional data if needed

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
        console.log(data);
        setTimeout(function() {
            if (this_modal) {
                this_modal.hide();
                $('.modal-backdrop.fade.show').hide();
            } else {
                console.error('Modal instance not found.');
            }
        }, 1000);

    })
    .catch(error => {
        console.error('Error:', error);
    });
});