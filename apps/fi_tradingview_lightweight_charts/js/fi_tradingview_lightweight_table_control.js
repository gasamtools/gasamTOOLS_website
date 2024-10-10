document.addEventListener("DOMContentLoaded", () => {
    if (!$('#ftlc_key_form').length) {

        const timeIntervalSelect = document.getElementById('timeIntervalSelect');
        const daysOfDataInput = document.getElementById('daysOfDataInput');

        var buttons = document.getElementsByClassName('btn gasam ftlc tbl');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].addEventListener('click', function(event) {
                let firstClass = event.target.classList[0];
                let secondClass = event.target.classList[1];
                let thirdClass = event.target.classList[2];
                indicator_params = {
                    'indicator': secondClass,
                    'sub_indicator': thirdClass,
                }
                timeIntervalSelect.value = firstClass;
                clearInterval(updateChart);
                updateChartIni(daysOfDataInput.value, firstClass, indicator_params);
            });
        }
    }
});