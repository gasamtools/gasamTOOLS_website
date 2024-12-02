document.addEventListener("DOMContentLoaded", () => {
    if ($('#FZAupdateChartButton').length) {
        $('#FZAupdateChartButton').on("click", function () {
            if (GASAM_fi_zelf_ready) {
                FZfetcherSelectPair();
            }
        });
    }
});

function FZfetcherSelectPair() {
    $('#FZAupdateChartButton').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
    $('#FZAupdateChartButton').prop('disabled', true);
    var chosen_pair = $('#FZAtradingPairSelect').val();
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'fz_fetcher');
    formData.append('js_function_sub', 'selectPair');
    formData.append('pair', chosen_pair);


    fetch(GASAM_fi_zelf_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        // update button
        $('#FZAupdateChartButton').html('Choose Pair');
        $('#FZAupdateChartButton').prop('disabled', false);

        // update feed
        FZcrystalUpdateFeed('#fz_alchemy_feed', data['status']);

        // update bank
        FZcrystalUpdateBank(data['bank_values_data']);

        if (data['ready_to_feed']) {
            $('#FZAfeederPanel').css('display', 'flex').hide().slideDown();
            $('.FZAfeederPanelBtn').prop('disabled', false);
            // reset FEEDER for fz_feeder.js
            feederCycle = 0
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}