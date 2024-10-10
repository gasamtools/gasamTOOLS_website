
const toolTip = document.createElement('div');
toolTip.classList.add('gasam', 'ftlc', 'tt');

// Global variables to store chart and series
let chart, candleSeries, maSeries, updateChart;

function updateChartIni(daysOfDataInput, timeIntervalSelect, indicator_params) {
    dataStream(parseInt(daysOfDataInput), timeIntervalSelect, indicator_params); // Fetch new data every interval
    const updateInterval = 5000; // Update every 6 seconds (adjust as needed)
    updateChart = setInterval(() => {
        dataStream(parseInt(daysOfDataInput), timeIntervalSelect, indicator_params); // Fetch new data every interval
        //console.log('update');
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



function dataStream(daysOfData, chartResolution, indicator_params) {

    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    const formObject = {
        'js_function': 'fi_tradingview_lightweight_charts_load',
        'daysOfData': daysOfData,
        'chartResolution': chartResolution,

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
            chart.subscribeCrosshairMove(updateTooltip);

            // SET TABLES VALUES
            setTableValueSMA(aggregate_data['ma_1day_last']['ma_marker'], '1day');
            setTableValueSMA(aggregate_data['ma_1week_last']['ma_marker'], '1week');

            if (indicator_params['indicator'] === 'sma') {
                // PRINT MA indicator and MARKERS
                maSeries.setData(aggregate_data['ma_data']);
                printMAMarkers(aggregate_data['ma_data'], candleSeries);
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
function updateTooltip(param) {
//    if (!param.time || param.point.x < 0 || param.point.y < 0) {
//        toolTip.style.display = 'none';
//        return;
//    }

    const dateStr = new Date(param.time * 1000).toLocaleDateString();
    //toolTip.style.display = 'block';
    const dataPoint = param.seriesData.get(candleSeries);
    if (typeof dataPoint != 'undefined') {
        toolTip.innerHTML = `
            <div style="color: ${'#2962FF'}">BTC-USDT</div>
            <div>Open: ${Math.round(dataPoint.open * 100) / 100}</div>
            <div>High: ${Math.round(dataPoint.high * 100) / 100}</div>
            <div>Low: ${Math.round(dataPoint.low * 100) / 100}</div>
            <div>Close: ${Math.round(dataPoint.close * 100) / 100}</div>
            <div>${dateStr}</div>
        `;
    }
}


function setTableValueSMA(data, interval) {
    $('.btn.gasam.ftlc.tbl.sma.'+interval).removeClass('bear');
    $('.btn.gasam.ftlc.tbl.sma.'+interval).removeClass('bull');
    $('.btn.gasam.ftlc.tbl.sma.'+interval).html(data);
    $('.btn.gasam.ftlc.tbl.sma.'+interval).addClass(data);
}


function drawLine(chart, color, lineWidth, data) {
    const lineSeries = chart.addLineSeries({
        color: color,
        lineWidth: lineWidth,
    });

    // Set data
    lineSeries.setData(data);


}


