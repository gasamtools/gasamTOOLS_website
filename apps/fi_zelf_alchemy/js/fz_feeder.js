let feederCycle, stopCycle;
feederCycle = 0; // start Cycle
stopCycle = false;

document.addEventListener("DOMContentLoaded", () => {
    if ($('#FZAfeederPanel').length) {
        $('.FZAfeederPanelBtn').on("click", function () {
            if (GASAM_fi_zelf_ready) {
                FZfeeder(this);
            }
        });
    }
});

function FZfeeder(bttn) {

    var elementId = $(bttn).attr('id');

    $('.FZAfeederPanelBtn').prop('disabled', false);
    if (elementId != 'stepForward') {
        $(bttn).prop('disabled', true);
    }

    if (elementId == 'pauseForward') {
        stopCycle = true;
    } else if (elementId == 'fastForward' || elementId == 'slowForward' || elementId == 'allForward') {
        stopCycle = false;
        FZfeederDataStream(elementId, feederCycle);
        FZcrystalUpdateFeed('#fz_alchemy_feed','<p>processing has begun...</p>');

    } else if (elementId == 'stepForward') {

        FZfeederDataStream(elementId, feederCycle);
    }
}


function FZfeederDataStream(elementId, Cycle) {

    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'fz_feeder');
    formData.append('js_function_sub', 'main');
    formData.append('command', elementId);
    formData.append('feederCycle', Cycle);
    formData.append('crystalSignalID', FZcrystalSignalID);
    formData.append('crystalSignalcommand', FZcrystalSignalcommand);


    fetch(GASAM_fi_zelf_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        // update alchemy feed
        FZcrystalUpdateFeed('#fz_alchemy_feed', data['alchemyFeed']);

        // update crystal feed
        FZcrystalUpdateFeed('#fz_crystal_feed', data['to_crystal']);

        // update bank
        FZcrystalUpdateBankSpot(data['bank_spot_values_data']);

        // update bank
        FZcrystalUpdateBankFutures(data['bank_futures_values_data']);

        // Print Candles
        FZcrystalPrintChartCandles(data['candles'], data['pair']);

        // Show/Hide signals via Crystal
        FZcrystalPrintSignals(data['printSignals']);
console.log(data);

        // updated feederCycle
        feederCycle = data['feederCycle']

        // STOP TEST WHEN END OF DATA
        if (data['end_of_test']) {
            $('.FZAfeederPanelBtn').prop('disabled', true);
            $('#stepForward').prop('disabled', false);
            stopCycle = true;
        }
        // Restart the interval after successful request
        if ((elementId == 'fastForward' || elementId == 'slowForward') && stopCycle === false) {
            FZfeederDataStream(elementId, feederCycle)
        }
    })
    .catch(error => {
        console.error('Error:', error);
        FZcrystalUpdateFeed('#fz_alchemy_feed', `<p>${error}</p>`);
    });
}
