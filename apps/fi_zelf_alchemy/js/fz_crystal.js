let chart, candleSeries, maSeries, toolTip;

document.addEventListener("DOMContentLoaded", () => {
    if ($('#chart').length) {
        FZcrystalInitializeChart();
    }
});

function FZcrystalInitializeChart() {
    // SETUP CHART

    const chartElement = document.getElementById('chart');

    toolTip = document.createElement('div');
    toolTip.classList.add('gasam', 'fz', 'tt');
    chartElement.appendChild(toolTip);

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

function FZcrystalPrintChartCandles(data, tradingPair) {
    // PRINT CANDLES
    candleSeries.setData(validateData(data));
    // PRINT CANDLE OPEN/CLOSE/LOW/HIGH
    const tooltipHandler = createTooltipHandler(tradingPair);
    chart.subscribeCrosshairMove(tooltipHandler);
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
                <div style="color: #2962FF">${tradingPair} | DAILY</div>
                <div>Open: ${(dataPoint.open).toFixed(2)}</div>
                <div>High: ${(dataPoint.high).toFixed(2)}</div>
                <div>Low: ${(dataPoint.low).toFixed(2)}</div>
                <div>Close: ${(dataPoint.close).toFixed(2)}</div>
                <div>${dateStr}</div>
            `;
        }
    };
}

function FZcrystalUpdateFeed(target, data) {
    var feed = $(target).html();
    $(target).html(feed+data);
    $(target).scrollTop($(target)[0].scrollHeight);
}

function FZcrystalUpdateBank(data) {

    // print total html
    $('#FZbankTotal').html(data['total']);

    // print coins html
    var html;
    html = '<div class="gasam fz container bank-coins" id="FZbankCoins">';
        html += '<table style="border-collapse: collapse; width: 50px;">';
            html += '<thead>';
                html += '<tr id="FZbankTableHeader">';
                    for (let coin of data['coins_data']) {
                        html +=`<th class="gasam fz bank-header"><span id="FZbankHeader${coin['currency']}">${coin['currency']}</span></th>`;

                    }
                html += '</tr>';
            html += '</thead>';
            html += '<tbody>';
                html += '<tr id="FZbankTableCell">';
                    for (let coin of data['coins_data']) {
                        html +=`<td class="gasam fz bank-cell"><span id="FZbankCell${coin['amount']}">${coin['amount']}</span></td>`;
                    }
                html += '</tr>';
            html += '</tbody>';
        html += '</table>';
    html += '</div>';

    $('#FZbankCoins').html(html);
}