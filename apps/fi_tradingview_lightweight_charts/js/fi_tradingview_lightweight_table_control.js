document.addEventListener("DOMContentLoaded", () => {
    if (!$('#ftlc_key_form').length) {

        const timeIntervalSelect = document.getElementById('timeIntervalSelect');
        const daysOfDataInput = document.getElementById('daysOfDataInput');
        const tradingPairSelect = document.getElementById('tradingPairSelect');

        var buttons = document.getElementsByClassName('btn gasam ftlc tbl');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].addEventListener('click', function(event) {
                let firstClass = event.target.classList[0];
                let secondClass = event.target.classList[1];
                let thirdClass = event.target.classList[2];
                let fourthClass = event.target.classList[3];
                indicator_params = {
                    'indicator': secondClass,
                    'sub_indicator': thirdClass,
                    'trend_indicator': fourthClass,
                    'interval_indicator': firstClass
                }

                timeIntervalSelect.value = firstClass;
                clearInterval(updateChart);
                updateChartIni(tradingPairSelect.value, daysOfDataInput.value, firstClass, indicator_params);
            });
        }
    }
});