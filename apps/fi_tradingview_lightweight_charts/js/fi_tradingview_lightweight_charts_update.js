document.addEventListener("DOMContentLoaded", () => {
    if (!$('#ftlc_key_form').length) {
        const updateChartButton = document.getElementById('updateChartButton');
        const timeIntervalSelect = document.getElementById('timeIntervalSelect');
        const tradingPairSelect = document.getElementById('tradingPairSelect');
        const daysOfDataInput = document.getElementById('daysOfDataInput');

        const indicator_params = {}


        updateChartButton.addEventListener('click', function() {
            clearInterval(updateChart);
            updateChartIni(tradingPairSelect.value, daysOfDataInput.value, timeIntervalSelect.value, indicator_params);
        });
    }
});