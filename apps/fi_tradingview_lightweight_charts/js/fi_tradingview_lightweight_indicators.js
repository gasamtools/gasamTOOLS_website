function printMAMarkers(ma_data, candleSeries) {

    let markers = []; // Collect all markers here

    for (let i = 0; i < ma_data.length; i++) {

        if ('ma_marker' in ma_data[i]) {

            var position, color, text;

            if (ma_data[i]['ma_marker'] == 'bull') {
                color = '#51ff01';
                position = 'aboveBar';
                text = '↑'
            } else if (ma_data[i]['ma_marker'] == 'bear') {
                position = 'belowBar';
                color = '#ac0202';
                text = '↓'
            }

            // Collect marker
            markers.push({
                time: ma_data[i]['time'],
                position: position,
                color: color,
                shape: 'circle',
                text: text
            });
        }
    }

    // Set all markers at once after the loop
    candleSeries.setMarkers(markers);
}


function printMSMarkers(aggregate_data, candleSeries) {
    let markers = []; // Collect all markers here

    if (aggregate_data['ms_ath'] != null) {
        markers.push({
            time: aggregate_data['ms_ath']['time'],
            position: 'aboveBar',
            color: '#06a606',
            shape: 'circle',
            text: 'ATH '+aggregate_data['ms_ath']['high']
        });
    }

    if (aggregate_data['ms_ll'] != null) {
        markers.push({
            time: aggregate_data['ms_ll']['time'],
            position: 'belowBar',
            color: '#b10707',
            shape: 'circle',
            text: 'LL '+aggregate_data['ms_ll']['low']
        });
    }

    if (aggregate_data['ms_mh'] != null) {
        markers.push({
            time: aggregate_data['ms_mh']['time'],
            position: 'aboveBar',
            color: '#00d900',
            shape: 'circle',
            text: 'MH '+aggregate_data['ms_mh']['high']
        });
    }

     if (aggregate_data['ms_csl'] != null) {
        markers.push({
            time: aggregate_data['ms_csl']['time'],
            position: 'belowBar',
            color: '#ff0909',
            shape: 'square',
            text: 'CSL '+aggregate_data['ms_csl']['low']
        });
    }

    if (aggregate_data['ms_csh'] != null) {
        markers.push({
            time: aggregate_data['ms_csh']['time'],
            position: 'aboveBar',
            color: '#05ff05',
            shape: 'square',
            text: 'CSH '+aggregate_data['ms_csh']['high']
        });
    }

    if (aggregate_data['ms_nsh_csh'] != null) {
        markers.push({
            time: aggregate_data['ms_nsh_csh']['time'],
            position: 'aboveBar',
            color: '#000',
            shape: 'square',
            text: '> CSH '+aggregate_data['ms_nsh_csh']['high']
        });
    }

    if (aggregate_data['ms_nsl_csl'] != null) {
        markers.push({
            time: aggregate_data['ms_nsl_csl']['time'],
            position: 'belowBar',
            color: '#000',
            shape: 'square',
            text: 'MAKES HL'+aggregate_data['ms_nsl_csl']['low']
        });
    }

    if (aggregate_data['ms_nsh_br'] != null) {
        markers.push({
            time: aggregate_data['ms_nsh_br']['time'],
            position: 'aboveBar',
            color: '#000',
            shape: 'square',
            text: 'MAKES HH '+aggregate_data['ms_nsh_br']['high']
        });
    }

    if (aggregate_data['ms_mh_br'] != null) {
        markers.push({
            time: aggregate_data['ms_mh_br']['time'],
            position: 'aboveBar',
            color: '#e10cff',
            shape: 'square',
            text: 'BREAKS MH '+aggregate_data['ms_mh_br']['high']
        });
    }

    if (aggregate_data['ms_ath_br'] != null) {
        markers.push({
            time: aggregate_data['ms_ath_br']['time'],
            position: 'aboveBar',
            color: '#2900bb',
            shape: 'square',
            text: 'BREAKS ATH '+aggregate_data['ms_ath_br']['high']
        });
    }

    // Set all markers at once after the loop
    candleSeries.setMarkers(markers);
}

function printTMMarkers(tm_data, candleSeries, interval) {

//    let markers = []; // Collect all markers here
//    markers.push({
//        time: tm_data['prevTime'],
//        position: 'aboveBar',
//        color: '#000',
//        shape: 'square',
//        text: 'prevTR '+tm_data['prevTR']
//    });
//
//    markers.push({
//        time: tm_data['lastTime'],
//        position: 'aboveBar',
//        color: '#26a69a',
//        shape: 'arrowUp',
//        text: 'HD '+tm_data['absHighDiff']
//    });
//
//    markers.push({
//        time: tm_data['lastTime'],
//        position: 'belowBar',
//        color: '#ff6363',
//        shape: 'arrowDown',
//        text: 'LD '+tm_data['absLowDiff']
//    });
//
//    // Set all markers at once after the loop
//    candleSeries.setMarkers(markers);


//console.log(tm_data['mode_data']);
    if (tm_data['mode_data'].length !== 0) {

        // Add TM projection to chart data
        last_time_ts = chartMainData[chartMainData.length - 1]['time']
        ts_interval = last_time_ts - chartMainData[chartMainData.length - 2]['time']
        for (let i = 1; i <= 35; i++) {
            last_time_ts += ts_interval
            chartMainData.push({
              "close": 0,
              "high": 0,
              "low": 0,
              "open": 0,
              "time": last_time_ts,
              "volume": 0
            })
        }
        candleSeries.setData(chartMainData);

        let markers = []; // Collect all markers here

        // LOOP THROUGH EVERY MODE
        for (let marker of tm_data['mode_data']) {

            // DRAW LINE
            if (marker['time_start'] !== undefined) {
                var marker_data = [
                    { time: marker['time_start'], value: marker['value_start'] },   //startPoint
                    { time: marker['time_end'], value: marker['value_end'] },       //endPoint
                ];
                drawLine(chart, 'blue', 1, marker_data);
             }

            // LABEL LINE (first candle)
            if (marker['mode_label'] !== undefined) {
                markers.push({
                    time: marker['time_start'],
                    position: 'belowBar',
                    color: '#000',
                    shape: 'arrowUp',
                    text: marker['mode_label']
                });
            }

            // LABEL MODE CONFIRMATION
            if (marker['mode_confirmation_info'] !== undefined) {

                // LABEL EXPANSION
                markers.push({
                    time: marker['mode_confirmation_info']['prevTime'],
                    position: 'aboveBar',
                    color: '#000',
                    shape: 'square',
                    text: 'prevTR '+ marker['mode_confirmation_info']['prevTR']
                });

                markers.push({
                    time: marker['mode_confirmation_info']['lastTime'],
                    position: 'aboveBar',
                    color: '#26a69a',
                    shape: 'arrowUp',
                    text: 'HD '+ marker['mode_confirmation_info']['absHighDiff']
                });

                markers.push({
                    time: marker['mode_confirmation_info']['lastTime'],
                    position: 'belowBar',
                    color: '#ff6363',
                    shape: 'arrowDown',
                    text: 'LD '+ marker['mode_confirmation_info']['absLowDiff']
                });

                // LABEL LAST CANDLE
                if (marker['mode_confirmation_info']['conf_last_candle_close']) {
                    markers.push({
                        time: marker['mode_confirmation_info']['last_candle_close_time'],
                        position: 'belowBar',
                        color: '#8f8f8f',
                        shape: 'circle',
                        text: marker['mode_confirmation_info']['last_candle_close_mark']
                    });
                }

            }

            // DRAW PROJECTION LINES
            if (marker['mode_projection_info'] !== undefined) {

                // LINE for target_price_1
                var marker_data = [
                    { time: marker['mode_projection_info']['expiration'], value: marker['value_start'] },   //startPoint
                    { time: marker['mode_projection_info']['expiration'], value: marker['mode_projection_info']['target_price_1'] },       //endPoint
                ];
                drawLine(chart, 'red', 1, marker_data);

                // LINE for target_price_2
                var marker_data = [
                    { time: marker['mode_projection_info']['expiration'], value: marker['mode_projection_info']['target_price_1'] },   //startPoint
                    { time: marker['mode_projection_info']['expiration'], value: marker['mode_projection_info']['target_price_2'] },       //endPoint
                ];
                drawLine(chart, '#bb0', 1, marker_data);

                // LINE for target_price_3
                var marker_data = [
                    { time: marker['mode_projection_info']['expiration'], value: marker['mode_projection_info']['target_price_2'] },   //startPoint
                    { time: marker['mode_projection_info']['expiration'], value: marker['mode_projection_info']['target_price_3'] },       //endPoint
                ];
                drawLine(chart, 'green', 1, marker_data);
            }
        }

        // Set all markers at once after the loop
        candleSeries.setMarkers(markers);
    }
}