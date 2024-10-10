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

//            // Convert the timestamp to a GMT date
//            const date = new Date(parseInt(ma_data[i]['time'].toString() + '000'));
//            const gmtDate = new Date(date.toUTCString());
//
//            // Extract the year, month, and day in GMT
//            const year = gmtDate.getUTCFullYear();      // Year in GMT
//            const month = gmtDate.getUTCMonth() + 1;    // Month (0-based, so add 1)
//            const day = gmtDate.getUTCDate();           // Day in GMT
//            const hour = gmtDate.getUTCHours();         // Hour in GMT

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