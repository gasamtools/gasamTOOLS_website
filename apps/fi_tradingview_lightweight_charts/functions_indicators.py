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


def calculate_market_structure_series_data(candle_data, trend):

    if trend == 'bull':
        ms_ath = market_structure_sub_ms_ath(candle_data)
        ms_ll = market_structure_sub_ms_ll(candle_data, ms_ath)
        ms_mh = market_structure_sub_ms_mh(candle_data, ms_ll)
        ms_csl = market_structure_sub_ms_csl(candle_data)
        ms_csh = market_structure_sub_ms_csh(candle_data, ms_csl)
        ms_nsh_csh = market_structure_sub_ms_nsh_csh(candle_data, ms_csh)
        ms_nsl_csl = market_structure_sub_ms_nsl_csl(candle_data, ms_csl, ms_nsh_csh)
        ms_nsh_br = market_structure_sub_ms_nsh_br(candle_data, ms_nsl_csl)
        ms_mh_br = market_structure_sub_ms_mh_ath_br(candle_data, ms_mh, ms_csh)
        ms_ath_br = market_structure_sub_ms_mh_ath_br(candle_data, ms_ath, ms_csh)

    elif trend == 'bear':
        ms_ath = None
        ms_ll = None
        ms_mh = None
        ms_csl = None
        ms_csh = None
        ms_nsh_csh = None
        ms_nsl_csl = None
        ms_nsh_br = None
        ms_mh_br = None
        ms_ath_br = None

    return_data = {
        'ms_ath': ms_ath,
        'ms_ll': ms_ll,
        'ms_mh': ms_mh,
        'ms_csl': ms_csl,
        'ms_csh': ms_csh,
        'ms_nsh_csh': ms_nsh_csh,
        'ms_nsl_csl': ms_nsl_csl,
        'ms_nsh_br': ms_nsh_br,
        'ms_mh_br': ms_mh_br,
        'ms_ath_br': ms_ath_br,
    }

    return return_data


def market_structure_sub_ms_ath(candle_data):
    # Find the dictionary with the largest 'high' value
    ms_ath = max(candle_data, key=lambda x: x['high'])

    return ms_ath


def market_structure_sub_ms_ll(candle_data, ms_ath):
    ms_ll = min(
        (item for item in candle_data if item['time'] > ms_ath['time']),
        key=lambda x: x['low'],
        default=None  # In case no valid items exist
    )

    return ms_ll

def market_structure_sub_ms_mh(candle_data, ms_ll):
    # Filter data where 'time' is smaller than in 'lowest_low_after_highest'
    filtered_data = [item for item in candle_data if item['time'] <= ms_ll['time']]

    # Iterate over the filtered data in reverse to find the first candle/dictionary with a 'high'
    # that is higher than both the closest previous and next dictionaries in time
    for i in range(len(filtered_data) - 2, 0, -1):
        current_candle = filtered_data[i]
        previous_candle = filtered_data[i - 1]
        next_candle = filtered_data[i + 1]

        # Check if current 'high' is greater than both previous and next 'high'
        if current_candle['high'] > previous_candle['high'] and current_candle['high'] > next_candle['high']:
            first_candle = current_candle
            break
    else:
        first_candle = None  # No candle found that meets the condition

    ms_mh = first_candle
    return ms_mh


def market_structure_sub_ms_csl(candle_data):
    first_candle = None

    for i in range(len(candle_data) - 2, 0, -1):  # Start from the second-last and go backward
        current_candle = candle_data[i]
        previous_candle = candle_data[i - 1]
        next_candle = candle_data[i + 1]

        # Check if current 'high' is greater than both previous and next 'high'
        if current_candle['low'] < previous_candle['low'] and current_candle['low'] < next_candle['low']:
            if (first_candle):
                second_handle = current_candle
                break
            first_candle = current_candle

    else:
        second_handle = None  # No candle found that meets the condition

    ms_csl = second_handle
    return ms_csl

def market_structure_sub_ms_csh(candle_data, ms_csl):
    first_candle = None

    filtered_data = [item for item in candle_data if item['time'] <= ms_csl['time']]

    for i in range(len(filtered_data) - 2, 0, -1):  # Start from the second-last and go backward
        current_candle = filtered_data[i]
        previous_candle = filtered_data[i - 1]
        next_candle = filtered_data[i + 1]

        # Check if current 'high' is greater than both previous and next 'high'
        if current_candle['high'] > previous_candle['high'] and current_candle['high'] > next_candle['high']:
            first_candle = current_candle
            break

    else:
        first_candle = None  # No candle found that meets the condition

    ms_csh = first_candle
    return ms_csh

def market_structure_sub_ms_nsh_csh(candle_data, ms_csh):

    filtered_data = [item for item in candle_data if item['time'] > ms_csh['time']]

    for i in range(0, len(filtered_data) - 1):  # Start from the second-last and go backward
        current_candle = filtered_data[i]
        # Check if current 'high' is greater than both previous and next 'high'
        if current_candle['high'] > ms_csh['high']:
            first_candle = current_candle
            break

    else:
        first_candle = None  # No candle found that meets the condition

    ms_nsh_csh = first_candle

    return ms_nsh_csh


def market_structure_sub_ms_nsl_csl(candle_data, ms_csl, ms_nsh_csh):
    try:
        filtered_data = [item for item in candle_data if item['time'] > ms_nsh_csh['time']]
    except TypeError:
        filtered_data = []
        first_candle = None

    if len(filtered_data) == 1:
        first_candle = None
    else:
        for i in range(1, len(filtered_data) - 1):
            current_candle = filtered_data[i]
            previous_candle = filtered_data[i - 1]
            next_candle = filtered_data[i + 1]

            # Check if current 'high' is greater than both previous and next 'high'
            if current_candle['low'] < previous_candle['low'] and current_candle['low'] < next_candle['low']:
                first_candle = current_candle
                break
            else:
                first_candle = None

    if first_candle is not None and first_candle['low'] > ms_csl['low']:
        ms_nsl_csl = first_candle
    else:
        ms_nsl_csl = None

    return ms_nsl_csl


def market_structure_sub_ms_nsh_br(candle_data, ms_nsl_csl):

    #FIND NSH
    try:
        nsh_data = [item for item in candle_data if item['time'] <= ms_nsl_csl['time']]
    except TypeError:
        nsh_data = []
    for i in range(len(nsh_data) - 2, 0, -1):  # Start from the second-last and go backward
        current_candle = nsh_data[i]
        previous_candle = nsh_data[i - 1]
        next_candle = nsh_data[i + 1]

        # Check if current 'high' is greater than both previous and next 'high'
        if current_candle['high'] > previous_candle['high'] and current_candle['high'] > next_candle['high']:
            nsh_candle = current_candle
            break

    else:
        nsh_candle = None  # No candle found that meets the condition

    #FIND NSH_BR
    nsh_br = None
    try:
        nsh_br_data = [item for item in candle_data if item['time'] > ms_nsl_csl['time']]
    except TypeError:
        nsh_br_data = []

    if len(nsh_br_data) == 1:
        if nsh_br_data[0]['high'] > nsh_candle['high']:
            nsh_br = nsh_br_data[0]
    else:
        for i in range(0, len(nsh_br_data) - 1):  # Start from the second-last and go backward
            current_candle = nsh_br_data[i]
            # Check if current 'high' is greater than both previous and next 'high'

            if current_candle['high'] > nsh_candle['high']:
                nsh_br = current_candle
                break

    ms_nsh_br = nsh_br


    return ms_nsh_br


def market_structure_sub_ms_mh_ath_br(candle_data, compared_h, ms_csh):
    ms_compared_h_br = None

    filtered_data = [item for item in candle_data if item['time'] > ms_csh['time']]

    if len(filtered_data) == 1:
        if filtered_data[0]['high'] > compared_h['high']:
            ms_compared_h_br = filtered_data[0]
    else:
        for i in range(0, len(filtered_data) - 1):  # Start from the second-last and go backward
            current_candle = filtered_data[i]
            # Check if current 'high' is greater than both previous and next 'high'

            if current_candle['high'] > compared_h['high']:
                ms_compared_h_br = current_candle
                break

    return ms_compared_h_br


def calculate_time_mode_expansion_series_data(data):
    status = 'nope'

    currentTR = data[-1]['high'] - data[-1]['low']
    prevClose = data[-2]['close']
    prevHigh = data[-2]['high']
    prevLow = data[-2]['low']
    prevTR = prevHigh - prevLow

    absHighDiff = abs(data[-1]['high'] - prevClose)
    absLowDiff = abs(prevClose - data[-1]['low'])

    potentialBullishExpansion = absHighDiff > prevTR
    potentialBearishExpansion = absLowDiff > prevTR

    isBullishExpansionBar = potentialBullishExpansion and (data[-1]['close'] > data[-1]['open'])
    isBearishExpansionBar = potentialBearishExpansion and (data[-1]['close'] < data[-1]['open'])



    if isBullishExpansionBar:
        status = 'bull'
    elif isBearishExpansionBar:
        status = 'bear'

    info = {
        'status': status,
        'prevTR': round(prevTR, 2),
        'prevTime': data[-2]['time'],
        'absHighDiff': round(absHighDiff, 2),
        'absLowDiff': round(absLowDiff, 2),
        'lastTime': data[-1]['time'],
    }
    return info