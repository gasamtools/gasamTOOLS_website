if ($('#fzw_LoadingModal').length) {
    const modalLoadingElement = document.getElementById('fzw_LoadingModal');
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
    formData.append('js_function', 'app_ini');

    fetch(GASAM_fi_zelf_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(function() {
            if (this_modal) {
                this_modal.hide();
                $('.modal-backdrop.fade.show').hide();
                    GASAM_fi_zelf_ready = true;

            } else {
                console.error('Modal instance not found.');
            }
        }, 1000);

    })
    .catch(error => {
        console.error('Error:', error);
    });
}
