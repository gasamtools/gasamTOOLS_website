def calculate_moving_average_series_data(candle_data, ma_length):
    ma_data = []

    for i in range(len(candle_data)):
        if i < ma_length:
            # Add whitespace data points until MA can be calculated
            ma_data.append({'time': candle_data[i]['time']})
        else:
            # Calculate the moving average
            sum_close = 0
            for j in range(ma_length):
                sum_close += candle_data[i - j]['close']
            ma_value = sum_close / ma_length
            ma_data.append({'time': candle_data[i]['time'], 'value': ma_value})

            if ma_value <= candle_data[i]['low']:
                ma_data[i]['ma_marker'] = 'bull'
            else:
                ma_data[i]['ma_marker'] = 'bear'

    return ma_data

