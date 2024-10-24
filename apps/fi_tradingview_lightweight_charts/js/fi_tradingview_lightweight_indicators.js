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

function printTMMarkers(tm_data, candleSeries) {
    let markers = []; // Collect all markers here

console.log(tm_data);

    markers.push({
        time: tm_data['prevTime'],
        position: 'aboveBar',
        color: '#000',
        shape: 'square',
        text: 'prevTR '+tm_data['prevTR']
    });

    markers.push({
        time: tm_data['lastTime'],
        position: 'aboveBar',
        color: '#26a69a',
        shape: 'arrowUp',
        text: 'HD '+tm_data['absHighDiff']
    });

    markers.push({
        time: tm_data['lastTime'],
        position: 'belowBar',
        color: '#ff6363',
        shape: 'arrowDown',
        text: 'LD '+tm_data['absLowDiff']
    });

    // Set all markers at once after the loop
    candleSeries.setMarkers(markers);
}