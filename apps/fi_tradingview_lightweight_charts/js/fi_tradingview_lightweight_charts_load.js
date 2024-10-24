
const toolTip = document.createElement('div');
toolTip.classList.add('gasam', 'ftlc', 'tt');

// Global variables to store chart and series
let chart, candleSeries, maSeries, updateChart;

function updateChartIni(tradingPairSelect, daysOfDataInput, timeIntervalSelect, indicator_params) {
    dataStream(tradingPairSelect, parseInt(daysOfDataInput), timeIntervalSelect, indicator_params); // Fetch new data every interval
    const updateInterval = 5000; // Update every 6 seconds (adjust as needed)
    updateChart = setInterval(() => {
        dataStream(tradingPairSelect, parseInt(daysOfDataInput), timeIntervalSelect, indicator_params); // Fetch new data every interval
    }, updateInterval);
}

function initializeChart() {
    // SETUP CHART
    const chartElement = document.getElementById('chart');
    chart = LightweightCharts.createChart(chartElement, {
        width: chartElement.clientWidth,
        height: chartElement.clientHeight,
        layout: {
            background: { type: 'solid', color: '#ffffff' },
            textColor: '#333',
        },
        grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#cccccc',
        },
        timeScale: {
            borderColor: '#cccccc',
            timeVisible: true,
            secondsVisible: false,
        },
    });

    candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
    });

    maSeries = chart.addLineSeries({ color: '#2962FF', lineWidth: 1 });
}



function dataStream(tradingPair, daysOfData, chartResolution, indicator_params) {

    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    const formObject = {
        'js_function': 'fi_tradingview_lightweight_charts_load',
        'daysOfData': daysOfData,
        'chartResolution': chartResolution,
        'tradingPair': tradingPair,

    };

    fetch(GASAM_fi_tradingview_lightweight_charts_URL, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
        },
        body: JSON.stringify(formObject)
    })
    .then(response => {
        //console.log('Raw response:', response);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(text => {
        //console.log('Response text:', text);
        try {
            return JSON.parse(text);
        } catch (e) {
            console.error('Error parsing JSON:', e);
            throw e;
        }
    })
    .then(aggregate_data => {
        //console.log('Parsed data:', data);
        if (Array.isArray(aggregate_data['candle_data']) && aggregate_data['candle_data'].length > 0) {

            // Update chart data
            candleSeries.setData(validateData(aggregate_data['candle_data']));

            // PRINT CANDLE OPEN/CLOSE/LOW/HIGH
            const tooltipHandler = createTooltipHandler(tradingPair);
            chart.subscribeCrosshairMove(tooltipHandler);

            // SET TABLES VALUES
            setTableValueSMA(aggregate_data['ma_1day_last']['ma_marker'], '1day');
            setTableValueSMA(aggregate_data['ma_1week_last']['ma_marker'], '1week');
            var ms_data = {
                'ms_1day_bull': aggregate_data['ms_1day_bull'],
                'ms_1day_bear': aggregate_data['ms_1day_bear'],
                'ms_1week_bull': aggregate_data['ms_1week_bull'],
                'ms_1week_bear': aggregate_data['ms_1week_bear'],
            }
            setTableValueMS(ms_data);

            var tm_data = {
                'tm_1day_exp': aggregate_data['tm_1day_exp'],
                'tm_1week_exp': aggregate_data['tm_1week_exp'],
                'tm_1day_mode': aggregate_data['tm_1day_mode'],
                'tm_1week_mode': aggregate_data['tm_1week_mode'],
            }
            setTableValueTM(tm_data);


            if (indicator_params['indicator'] === 'sma') {
                // PRINT MA indicator and MARKERS
                maSeries.setData(aggregate_data['ma_data']);
                printMAMarkers(aggregate_data['ma_data'], candleSeries);
            } else if (indicator_params['indicator'] === 'ms') {
                // PRINT MS indicator and MARKERS
                maSeries.setData([]);

                if (indicator_params['interval_indicator'] == '1day') {
                    if (indicator_params['trend_indicator'] == 'bl') {
                        printMSMarkers(aggregate_data['ms_1day_bull'], candleSeries);
                    } else if (indicator_params['trend_indicator'] == 'br') {
                        printMSMarkers(aggregate_data['ms_1day_bear'], candleSeries);
                    }
                } else if (indicator_params['interval_indicator'] == '1week') {
                    if (indicator_params['trend_indicator'] == 'bl') {
                        printMSMarkers(aggregate_data['ms_1week_bull'], candleSeries);
                    } else if (indicator_params['trend_indicator'] == 'br') {
                        printMSMarkers(aggregate_data['ms_1week_bear'], candleSeries);
                    }
                }
            } else if (indicator_params['indicator'] === 'tm') {
                // PRINT MS indicator and MARKERS
                maSeries.setData([]);

                if (indicator_params['interval_indicator'] == '1day') {
                    if (indicator_params['sub_indicator'] == 'exp') {
                        printTMMarkers(aggregate_data['tm_1day_exp'], candleSeries);
//console.log(aggregate_data['tm_1day_exp']);
                    } else if (indicator_params['sub_indicator'] == 'mode') {
                        printTMMarkers(aggregate_data['tm_1day_mode'], candleSeries);
//console.log(aggregate_data['tm_1day_mode']);
                    }
                } else if (indicator_params['interval_indicator'] == '1week') {
                    if (indicator_params['sub_indicator'] == 'exp') {
                        printTMMarkers(aggregate_data['tm_1week_exp'], candleSeries);
//console.log(aggregate_data['tm_1week_exp']);
                    } else if (indicator_params['sub_indicator'] == 'mode') {
                        printTMMarkers(aggregate_data['tm_1week_mode'], candleSeries);
//console.log(aggregate_data['tm_1week_mode']);
                    }
                }
            } else {
                maSeries.setData([]);
                candleSeries.setMarkers([]);
            }





            // Other chart elements (markers, price lines, etc.) can be updated here if needed

            //chart.timeScale().fitContent();

            //const recentCandlePosition = data.length - 100; // Most recent candle is at the last index
            //chart.timeScale().scrollToPosition(10);

            // DrawLine
//            var marker_data = [
//                { time: '2024-08-01', value: 60000 },   //startPoint
//                { time: '2024-08-12', value: 65000 },   //endPoint
//            ];
            //drawLine(chart,'blue',1, marker_data)

            // DRAW PRICE LINE
//            const priceLine = candleSeries.createPriceLine({
//                price: 60000,
//                color: 'black',
//                lineWidth: 2,
//                lineStyle: LightweightCharts.LineStyle.Dotted,
//                axisLabelVisible: true,
//                title: 'P/L 500',
//            });


        } else {
            console.error('Received empty or invalid data');
        }
    })
    .catch(error => console.error('Error:', error));
}


function validateData(data) {
    const validData = data.filter(dataPoint => {
      if (!dataPoint || dataPoint.time == null || dataPoint.open == null ||
          dataPoint.high == null || dataPoint.low == null || dataPoint.close == null) {
            console.error('Invalid data point:', dataPoint);
        return false;
      }
      return true;
    });

    return validData;
}


// Update tooltip content and position
function createTooltipHandler(tradingPair) {
    // Return a closure that has access to tradingPair
    return function updateTooltip(param) {
        // Return if no valid crosshair position
        if (!param.time || param.point.x < 0 || param.point.y < 0) {
            toolTip.style.display = 'none';
            return;
        }

        const dateStr = new Date(param.time * 1000).toLocaleDateString();
        const dataPoint = param.seriesData.get(candleSeries);

        if (dataPoint) {
            toolTip.style.display = 'block';
            toolTip.innerHTML = `
                <div style="color: #2962FF">${tradingPair}</div>
                <div>Open: ${(dataPoint.open).toFixed(2)}</div>
                <div>High: ${(dataPoint.high).toFixed(2)}</div>
                <div>Low: ${(dataPoint.low).toFixed(2)}</div>
                <div>Close: ${(dataPoint.close).toFixed(2)}</div>
                <div>${dateStr}</div>
            `;
        }
    };
}


function setTableValueSMA(data, interval) {
    $('.btn.gasam.ftlc.tbl.sma.'+interval).removeClass('bear');
    $('.btn.gasam.ftlc.tbl.sma.'+interval).removeClass('bull');
    $('.btn.gasam.ftlc.tbl.sma.'+interval).html(data);
    $('.btn.gasam.ftlc.tbl.sma.'+interval).addClass(data);
}

function setTableValueMS(data) {

    $('.btn.gasam.ftlc.tbl.ms').removeClass('bear');
    $('.btn.gasam.ftlc.tbl.ms').removeClass('bull');

    var interval, trend;

    for (let key in data) {

        if (key.includes('1week')) {
            interval = '1week';
        } else if (key.includes('1day')) {
            interval = '1day';
        }

        if (key.includes('bull')) {
            trend = 'bl';
        } else if (key.includes('bear')) {
            trend = 'br';
        }

        let fieldNames = ['ms_nsh_csh', 'ms_nsl_csl', 'ms_nsh_br', 'ms_mh_br', 'ms_ath_br'];

        fieldNames.forEach(function(fieldName) {
            let element = $('.' + fieldName + '.btn.gasam.ftlc.tbl.ms.' + interval + '.' + trend);

            if (data[key][fieldName] != null) {
                element.html('VALIDATED');
                element.addClass('bull');
            } else {
                element.html('NOT VALIDATED');
                element.addClass('bear');
            }
        });
    }
}

function setTableValueTM(tm_data) {
    $('.btn.gasam.ftlc.tbl.tm').removeClass('bear');
    $('.btn.gasam.ftlc.tbl.tm').removeClass('bull');
    $('.btn.gasam.ftlc.tbl.tm').removeClass('nope');

    $('.btn.gasam.ftlc.tbl.tm.exp.1day').html(tm_data['tm_1day_exp']['status']);
    $('.btn.gasam.ftlc.tbl.tm.exp.1day').addClass(tm_data['tm_1day_exp']['status']);
    $('.btn.gasam.ftlc.tbl.tm.exp.1week').html(tm_data['tm_1week_exp']['status']);
    $('.btn.gasam.ftlc.tbl.tm.exp.1week').addClass(tm_data['tm_1day_exp']['status']);
}


function drawLine(chart, color, lineWidth, data) {
    const lineSeries = chart.addLineSeries({
        color: color,
        lineWidth: lineWidth,
    });

    // Set data
    lineSeries.setData(data);


}


