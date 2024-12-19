let chart, candleSeries, maSeries, toolTip, hideSignal;
let lineSeriesArray = [];
let markers = [];
let FZcrystalSignalID, FZcrystalSignalcommand = false;

document.addEventListener("DOMContentLoaded", () => {
    if ($('#chart').length) {
        FZcrystalInitializeChart();
    }
    if ($('#FZhideSignal').length) {
        $('.gasam.fz.app-container.row.body').on( 'click', '.fz.crystal.signal', function( event ) {
            FZcrystalShowHideSignal($(this).attr('id'));
        });
    }
});


function FZcrystalInitializeChart() {
    // SETUP CHART

    const chartElement = document.getElementById('chart');

    toolTip = document.createElement('div');
    toolTip.classList.add('gasam', 'fz', 'tt');
    chartElement.appendChild(toolTip);

    hideSignal = document.createElement('button');
    hideSignal.classList.add('gasam', 'fz', 'crystal', 'signal', 'hideSignal');
    hideSignal.id = 'FZhideSignal';
    hideSignal.innerHTML = 'Hide Signals';
    chartElement.appendChild(hideSignal);

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

        const dateStr = new Date(param.time * 1000).toLocaleDateString("en-US", { timeZone: "UTC" });
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
    $(target).hover(
        // Mouse enter
        function() {
            // Disable auto-scrolling when mouse is over the div
            $(this).data('hover', true);
        },
        // Mouse leave
        function() {
            // Re-enable auto-scrolling when mouse leaves the div
            $(this).data('hover', false);
        }
    );

    $(target).append(data);

    // Check if not hovering before scrolling
    if (!$(target).data('hover')) {
        $(target).scrollTop($(target)[0].scrollHeight);
    }
}

function FZcrystalUpdateBankSpot(data) {

    // print total html
    $('#FZbankSpotTotal').html(data['total']);

    // print coins html
    var html;
    html = '<table style="border-collapse: collapse; width: 50px;">';
        html += '<thead>';
            html += '<tr id="FZbankTableSpotHeader">';
                for (let coin of data['coins_data']) {
                    html +=`<th class="gasam fz bank-header"><span id="FZbankHeaderSpot${coin['currency']}">${coin['currency']}</span></th>`;

                }
            html += '</tr>';
        html += '</thead>';
        html += '<tbody>';
            html += '<tr id="FZbankTableSpotCell">';
                for (let coin of data['coins_data']) {
                    html +=`<td class="gasam fz bank-cell"><span id="FZbankSpotCell${coin['amount']}">${coin['amount']}</span></td>`;
                }
            html += '</tr>';
        html += '</tbody>';
    html += '</table>';

    $('#FZbankSpotCoins').html(html);
}

function FZcrystalUpdateBankFutures(data) {

    // print total html
    $('#FZbankFuturesTotal').html(data['total']);

    // print coins html
    var html;
    html = '<table style="border-collapse: collapse;">';
        html += '<thead>';
            html += '<tr id="FZbankTableFuturesHeader">';
                for (let coin of data['coins_data']) {
                    html +=`<th class="gasam fz bank-header"><span id="FZbankHeaderFutures${coin['currency']}">#${coin['trade_id']} ${coin['currency']}-${coin['trade_position']}</span></th>`;
                }
            html += '</tr>';
        html += '</thead>';
        html += '<tbody>';
            html += '<tr id="FZbankTableFuturesCell">';
                for (let coin of data['coins_data']) {
                    html +=`<td class="gasam fz bank-cell"><span id="FZbankCellFutures${coin['amount']}">${coin['amount']}&nbsp;</span>|<span>&nbsp;${coin['pnl']}</span></td>`;
                }
            html += '</tr>';
        html += '</tbody>';
    html += '</table>';

    $('#FZbankFuturesCoins').html(html);
}


function FZcrystalClearAllLines(chart) {
    lineSeriesArray.forEach(lineSeries => chart.removeSeries(lineSeries));
    lineSeriesArray.length = 0; // Clear the array of references
}

function FZcrystalShowHideSignal(id) {
    if (id == 'FZhideSignal') {
        FZcrystalSignalcommand = false;
        maSeries.setData('');
        candleSeries.setMarkers([]);
    } else {
        FZcrystalSignalcommand = true;
        FZcrystalSignalID = id;
        document.getElementById('stepForward').click();
    }
}

function FZcrystalPrintSignals(signalData) {

    markers = []
    if (FZcrystalSignalcommand == false) {
        maSeries.setData('');
        FZcrystalClearAllLines(chart);
        candleSeries.setMarkers([]);
    } else if (signalData['signal_type'] == 'SMA50') {
        //console.log(signalData);
        maSeries.setData(signalData['ma_data']);

        markers.push({
            time: parseInt(signalData['sdp_0'], 10),
            position: 'belowBar',
            color: '#000',
            shape: 'square',
            text: 'Start '+ signalData['trend_type']
        });

        if (signalData['sdp_1'] !== null) {
            markers.push({
                time: parseInt(signalData['sdp_1'], 10),
                position: 'aboveBar',
                color: '#000',
                shape: 'circle',
                text: 'End '+ signalData['trend_type']
            });
        }

        if (signalData['trades'].length) {
            signalData['trades'].forEach(function(element) {
                if (element['trade_action'] == 'sell') {
                    var position = 'belowBar';
                    var color = "#454545"
                    var shape = 'arrowDown'
                    var text = 'Sell @'+element['price']
                } else if (element['trade_action'] == 'buy') {
                    var position = 'aboveBar'
                    var color = "#00bd9a"
                    var shape = 'arrowUp'
                    var text = 'Buy @'+element['price']
                }
                markers.push({
                    time: parseInt(element['tdp_1'], 10),
                    position: position,
                    color: color,
                    shape: shape,
                    text: text
                });
            });
        }


        candleSeries.setMarkers(markers);
    }
}
