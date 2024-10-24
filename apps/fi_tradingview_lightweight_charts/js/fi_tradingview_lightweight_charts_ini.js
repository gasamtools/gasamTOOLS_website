if (!$('#ftlc_key_form').length) {
    const modalLoadingElement = document.getElementById('fi_tradingview_lightweight_chartsLoadingModal');
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
    formData.append('js_function', 'fi_tradingview_lightweight_charts_ini'); // Append additional data if needed

    fetch(GASAM_fi_tradingview_lightweight_charts_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(function() {
            if (this_modal) {
                this_modal.hide();
                $('.modal-backdrop.fade.show').hide();

                    const chartContainer = document.getElementById('chart');
                    chartContainer.appendChild(toolTip);
                    initializeChart();
                    // Initial data fetch
                    // Set up interval to fetch data periodically
                    const indicator_params = {}
                    updateChartIni('BTC-USDT', 1000, '1day', indicator_params);

            } else {
                console.error('Modal instance not found.');
            }
        }, 1000);

    })
    .catch(error => {
        console.error('Error:', error);
    });
}
