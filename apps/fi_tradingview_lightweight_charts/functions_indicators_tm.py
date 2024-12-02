def calculate_time_mode_mode_screener(data, ):
    #{'time': 1705881600, 'open': 41579.9, 'high': 42839.0, 'low': 38559.0, 'close': 42037.9, 'volume': 21290.97058559}

    modes_info = []

    macro_mode_info = find_macro_mode(data)
    closest_mode_info = find_closest_mode(data)
    # biggest_mode_info = find_biggest_mode(data)

    #
    if macro_mode_info['LL']['mode_setup_valid']:
        macro_mode_info['LL']['mode_confirmation_info'] = time_mode_find_mode_confirmation(macro_mode_info['LL'], data)
        macro_mode_info['LL']['mode_confirmation_valid'] = macro_mode_info['LL']['mode_confirmation_info']['conf_mode']
    if macro_mode_info['HH']['mode_setup_valid']:
        macro_mode_info['HH']['mode_confirmation_info'] = time_mode_find_mode_confirmation(macro_mode_info['HH'], data)
        macro_mode_info['HH']['mode_confirmation_valid'] = macro_mode_info['HH']['mode_confirmation_info']['conf_mode']

    if closest_mode_info['LL']['mode_setup_valid']:
        closest_mode_info['LL']['mode_confirmation_info'] = time_mode_find_mode_confirmation(closest_mode_info['LL'], data)
        closest_mode_info['LL']['mode_confirmation_valid'] = closest_mode_info['LL']['mode_confirmation_info']['conf_mode']
    if closest_mode_info['HH']['mode_setup_valid']:
        closest_mode_info['HH']['mode_confirmation_info'] = time_mode_find_mode_confirmation(closest_mode_info['HH'], data)
        closest_mode_info['HH']['mode_confirmation_valid'] = closest_mode_info['HH']['mode_confirmation_info']['conf_mode']
    # if biggest_mode_info['mode_setup_valid']:
    #     biggest_mode_info['mode_confirmation_info'] = time_mode_find_mode_confirmation(biggest_mode_info)

    if 'mode_confirmation_valid' in macro_mode_info['LL'] and macro_mode_info['LL']['mode_confirmation_valid']:
        macro_mode_info['LL']['mode_projection_info'] = time_mode_find_mode_projection(macro_mode_info['LL'], data)
    if 'mode_confirmation_valid' in macro_mode_info['HH'] and macro_mode_info['HH']['mode_confirmation_valid']:
        macro_mode_info['HH']['mode_projection_info'] = time_mode_find_mode_projection(macro_mode_info['HH'], data)

    if 'mode_confirmation_valid' in closest_mode_info['LL'] and closest_mode_info['LL']['mode_confirmation_valid']:
        closest_mode_info['LL']['mode_projection_info'] = time_mode_find_mode_projection(closest_mode_info['LL'], data)
    if 'mode_confirmation_valid' in closest_mode_info['HH'] and closest_mode_info['HH']['mode_confirmation_valid']:
        closest_mode_info['HH']['mode_projection_info'] = time_mode_find_mode_projection(closest_mode_info['HH'], data)
    # if biggest_mode_info['mode_confirmation_valid']:
    #     biggest_mode_info['mode_projection_info'] = time_mode_find_mode_projection(biggest_mode_info)

    modes_info.append(macro_mode_info['LL'])
    modes_info.append(macro_mode_info['HH'])
    modes_info.append(closest_mode_info['LL'])
    modes_info.append(closest_mode_info['HH'])
    # modes_info.append(biggest_mode_info)

    #FILTER OUT MODES WITH THE SAME MODE PRICE BASED ON HIGHER MODE SIZE
    modes_info = filter_same_mode_price(modes_info)
    # FILTER OUT MODES WITH THE SAME START TIMESTAMP BASED ON LONGER MODE SIZE
    modes_info = filter_same_start_timestamp(modes_info)

    return modes_info


def find_macro_mode(data):
    # LOOKING FOR MACRO MODE
    # Only work on a 40 bar range from the most recent candle
    # Find the lowest low of the range
    # Scan for the mode from LL to most recent
    # If the mode is found (>= 5 bars) but is more than >20 bars, label as “NOISY BULL”
    # Find the highest high of the range
    # Scan for the mode from HH to most recent
    # If the mode is found (>= 5 bars) but is more than >20 bars, label as “NOISY BEAR”

    macro_mode_info = {
        'LL': {'mode_setup_valid': False},
        'HH': {'mode_setup_valid': False}
    }

    # Find the lowest low and the highest high of the range
    lowest_low = 0
    lowest_low_index = 0
    highest_high = 0
    highest_high_index = 0
    maximum_range = 40
    macro_mode_info = macro_mode_info | {'start_candle': data[len(data) - maximum_range - 1]}

    for i in range(len(data) - 1, -1, -1):

        if maximum_range == 40:
            lowest_low = data[i]['low']
            lowest_low_index = i
            highest_high = data[i]['high']
            highest_high_index = i

        prev_candle_low = data[i - 1]['low']
        prev_candle_high = data[i - 1]['high']

        if prev_candle_low < lowest_low:
            lowest_low, lowest_low_index = prev_candle_low, i - 1

        if prev_candle_high > highest_high:
            highest_high, highest_high_index = prev_candle_high, i - 1

        maximum_range -= 1

        if maximum_range == 0:
            break

    macro_mode_info['LL'] = macro_mode_info['LL'] | {
        'lowest_low': lowest_low,
        'lowest_low_candle': data[lowest_low_index],
    }
    macro_mode_info['HH'] = macro_mode_info['HH'] | {
        'highest_high': highest_high,
        'highest_high_candle': data[highest_high_index]
    }

    # Scan for the mode from LL to most recent
    last_index = len(data) - 1
    if last_index - lowest_low_index >= 5:
        ll_found_mode = time_mode_find_mode(data, lowest_low_index, last_index)
        ll_mode_price = ll_found_mode['mode_price']
        ll_number_candles_in_mode = ll_found_mode['mode_end_candle_index'] - ll_found_mode['mode_start_candle_index']
        ll_number_candles_crossing_mode = ll_found_mode['number_candles_in_mode']
        ll_mode_start_candle_index = ll_found_mode['mode_start_candle_index']
        ll_mode_end_candle_index = ll_found_mode['mode_end_candle_index']
    else:
        ll_mode_price, ll_number_candles_in_mode, ll_number_candles_crossing_mode, ll_mode_start_candle_index, ll_mode_end_candle_index = None, None, None, None, None

    # Scan for the mode from HH to most recent
    if last_index - highest_high_index >= 5:
        hh_found_mode = time_mode_find_mode(data, highest_high_index, last_index)
        hh_mode_price = hh_found_mode['mode_price']
        hh_number_candles_in_mode = hh_found_mode['mode_end_candle_index'] - hh_found_mode['mode_start_candle_index']
        hh_number_candles_crossing_mode = hh_found_mode['number_candles_in_mode']
        hh_mode_start_candle_index = hh_found_mode['mode_start_candle_index']
        hh_mode_end_candle_index = hh_found_mode['mode_end_candle_index']
    else:
        hh_mode_price, hh_number_candles_crossing_mode, hh_mode_start_candle_index, hh_mode_end_candle_index = None, None, None, None

    # If the mode is found (>= 5 bars) but is more than >20 bars, label as “NOISY BULL”
    if ll_number_candles_crossing_mode:
        if ll_number_candles_crossing_mode >= 5:
            macro_mode_info['LL']['mode_setup_valid'] = True
            macro_mode_info['LL'] = macro_mode_info['LL'] | {
                'mode_label': f'MACRO BULL mode_size: {ll_number_candles_crossing_mode}/{ll_number_candles_in_mode}',
                'time_start': data[ll_mode_start_candle_index]['time'],
                'value_start': ll_mode_price,
                'time_end': data[ll_mode_end_candle_index]['time'],
                'value_end': ll_mode_price,
            }
            if ll_number_candles_crossing_mode >= 20:
                macro_mode_info['LL'][
                    'mode_label'] = f'MACRO NOISY BULL mode_size: {ll_number_candles_crossing_mode}/{ll_number_candles_in_mode}'

    # If the mode is found (>= 5 bars) but is more than >20 bars, label as “NOISY BEAR”
    if hh_number_candles_crossing_mode:
        if hh_number_candles_crossing_mode >= 5:
            macro_mode_info['HH']['mode_setup_valid'] = True
            macro_mode_info['HH'] = macro_mode_info['HH'] | {
                'mode_label': f'MACRO BEAR mode_size: {hh_number_candles_crossing_mode}/{hh_number_candles_in_mode}',
                'time_start': data[hh_mode_start_candle_index]['time'],
                'value_start': hh_mode_price,
                'time_end': data[hh_mode_end_candle_index]['time'],
                'value_end': hh_mode_price,
            }

            if hh_number_candles_crossing_mode >= 20:
                macro_mode_info['HH'][
                    'mode_label'] = f'MACRO NOISY BEAR mode_size: {hh_number_candles_crossing_mode}/{hh_number_candles_in_mode}'

    return macro_mode_info


def find_closest_mode(data):
    # LOOKING FOR MICRO MODE
    # Start scan from for the last 5 candles of chart
    # Check the low of each candle. If the low of the current candle is lower than 4 candles after it - start scanning for mode.
    # Find mode price - if 5 candles touch it, then the mode is found
    # Record the very last candle that touches the mode and size of the mode
    # Repeat first five steps for the highest high
    # Show the closest mode (ends on the most recent candle)

    def find_mode_extension_left(data, start_candle, start_candle_param, type):
        s = start_candle
        index = s
        can_extend = True

        limit = 11
        while can_extend:
            limit -= 1
            if type == 'low':
                if start_candle_param > data[s - 1]['low']:
                    start_candle_param = data[s - 1]['low']
                    index = s - 1

            elif type == 'high':
                if start_candle_param < data[s - 1]['high']:
                    start_candle_param = data[s - 1]['high']
                    index = s - 1

            s -= 1
            if limit == 0:
                can_extend = False

        return index

    def find_mode_extension_right(data, i, start_candle_param, type):
        index = i
        can_extend = True

        while can_extend:
            if i + 1 < len(data):
                if type == 'low':
                    if start_candle_param < data[i + 1]['low']:
                        index = i + 1
                        i += 1
                    else:
                        can_extend = False
                elif type == 'high':
                    if start_candle_param > data[i + 1]['high']:
                        index = i + 1
                        i += 1
                    else:
                        can_extend = False
            else:
                can_extend = False

        return index

    def record_mode(label, this_mode_info, found_mode, end_scan, start_scan):
        import math

        if found_mode['number_candles_in_mode'] >= 5:
            mode_price = found_mode['mode_price']
            number_candles_crossing_mode = found_mode['number_candles_in_mode']

            # FILTER CANDLES TO THE RIGHT NOT TOUCHING THE MODE
            last_candle_in_mode = end_scan
            for i in range(last_candle_in_mode, start_scan, -1):
                if data[i]['low'] > 100:
                    if not math.floor(data[i]['low']) <= mode_price <= round(data[i]['high']):
                        end_scan -= 1
                    else:
                        break
                else:
                    if not data[i]['low'] < mode_price < data[i]['high']:
                        end_scan -= 1
                    else:
                        break

            # FILTER CANDLES TO THE LEFT NOT TOUCHING THE MODE
            first_candle_in_mode = start_scan
            for i in range(first_candle_in_mode, end_scan):
                if data[i]['low'] > 100:
                    if not math.floor(data[i]['low']) <= mode_price <= round(data[i]['high']):
                        start_scan += 1
                    else:
                        break
                else:
                    if not data[i]['low'] < mode_price < data[i]['high']:
                        start_scan += 1
                    else:
                        break

            number_candles_in_mode = (end_scan - start_scan) + 1

            if not this_mode_info['mode_setup_valid']:
                this_mode_info['mode_setup_valid'] = True
                this_mode_info = this_mode_info | {
                    'mode_label': f'CLOSEST {label} mode_size: {number_candles_crossing_mode}/{number_candles_in_mode}',
                    'time_start': data[start_scan]['time'],
                    'value_start': mode_price,
                    'time_end': data[end_scan]['time'],
                    'value_end': mode_price,
                }

        return this_mode_info

    closest_mode_info = {
        'LL': {'mode_setup_valid': False},
        'HH': {'mode_setup_valid': False}
    }

    mode_search_range = 5
    mode_price = 0
    for i in range(len(data) - 1, -1, -1):
        start_candle = i - (mode_search_range - 1)
        start_candle_low = data[start_candle]['low']
        start_candle_high = data[start_candle]['high']

        is_mode_ll = False
        for ii in range(start_candle, i + 1):
            if (start_candle_low > data[ii]['low']):
                is_mode_ll = False
                break
            else:
                is_mode_ll = True


        is_mode_hh = False
        for ii in range(start_candle, i + 1):
            if (start_candle_high < data[ii]['high']):
                is_mode_hh = False
                break
            else:
                is_mode_hh = True


        if is_mode_ll:
            start_scan = find_mode_extension_left(data, start_candle, start_candle_low, 'low')
            end_scan = find_mode_extension_right(data, i, start_candle_low, 'low')

            #print(f'passed start_scan {data[start_scan]} and end_scan {data[end_scan]}')
            found_mode = time_mode_find_mode(data, start_scan, end_scan)
            closest_mode_info['LL'] = record_mode('BULL', closest_mode_info['LL'], found_mode, end_scan, start_scan)

        if is_mode_hh:
            start_scan = find_mode_extension_left(data, start_candle, start_candle_high, 'high')
            end_scan = find_mode_extension_right(data, i, start_candle_high, 'high')
            found_mode = time_mode_find_mode(data, start_scan, end_scan)
            closest_mode_info['HH'] = record_mode('BEAR', closest_mode_info['HH'], found_mode, end_scan, start_scan)

        if closest_mode_info['LL']['mode_setup_valid'] and closest_mode_info['HH']['mode_setup_valid']:
            break

    closest_mode_info = filter_closest_mode(closest_mode_info)

    return closest_mode_info


def time_mode_find_mode(data, start_candle, end_candle):
    from collections import Counter
    import math
    number_candles_in_mode = 0

    def float_range(start, end, step):

        while start <= end:
            yield round(start, 10)  # Round to avoid floating-point precision issues
            start += step

    # Define the ranges with float step size
    ranges = []

    for ii in range(start_candle, end_candle + 1):
        if data[ii]['low'] > 100:
            ranges.append(float_range(math.floor(data[ii]['low']), round(data[ii]['high']), 1))
        else:
            ranges.append(float_range(round(data[ii]['low'], 2), round(data[ii]['high'], 2), 0.01))


    # Flatten the ranges and count occurrences of each number
    counter = Counter()
    for r in ranges:
        counter.update(r)

    # Find the number that appears in the most ranges
    mode_price, number_candles_in_mode = counter.most_common(1)[0]

    # Find first candle in the mode
    mode_start_candle_index = 0
    for i in range(start_candle, end_candle + 1):
        if data[i]['low'] < mode_price < data[i]['high']:
            mode_start_candle_index = i
            break

    # Find last candle in the mode
    mode_end_candle_index = 0
    for i in range(end_candle, start_candle - 1, -1):
        if data[i]['low'] > 100:
            if math.floor(data[i]['low']) <= mode_price <= round(data[i]['high']):
                mode_end_candle_index = i
                break
        else:
            if data[i]['low'] <= mode_price <= data[i]['high']:
                mode_end_candle_index = i
                break
    return {
        'mode_price': mode_price,
        'number_candles_in_mode': number_candles_in_mode,
        'mode_start_candle_index': mode_start_candle_index,
        'mode_end_candle_index': mode_end_candle_index
    }


def time_mode_find_mode_confirmation(mode_info, data):
    first_bar_out, last_bar_in, previous_bar_in = {}, {}, {}
    mode_price = mode_info['value_start']

    for i in range(len(data) - 1, -1, -1):
        # print(f"Index: {i}, Value: {data[i]}")
        if data[i]['time'] == mode_info['time_end']:
            last_bar_in = data[i]
            previous_bar_in = data[i - 1]
            if i + 2 < len(data):
                first_bar_out = data[i + 1]

    trend_confirmation_found = False
    expansion_info, trend_confirmation_info = {}, {}

    def find_expansion(previous_bar_in, last_bar_in):
        nonlocal trend_confirmation_found
        prevClose = previous_bar_in['close']
        prevHigh = previous_bar_in['high']
        prevLow = previous_bar_in['low']
        prevTR = prevHigh - prevLow

        absHighDiff = abs(last_bar_in['high'] - prevClose)
        absLowDiff = abs(prevClose - last_bar_in['low'])

        potentialBullishExpansion = absHighDiff > prevTR
        potentialBearishExpansion = absLowDiff > prevTR

        isBullishExpansionBar = potentialBullishExpansion and (last_bar_in['close'] > last_bar_in['open'])
        isBearishExpansionBar = potentialBearishExpansion and (last_bar_in['close'] < last_bar_in['open'])

        if isBullishExpansionBar:
            status = 'bull'
            trend_confirmation_found = True
        elif isBearishExpansionBar:
            status = 'bear'
            trend_confirmation_found = True
        else:
            status = 'nope'

        expansion_info = {
            'conf_mode': trend_confirmation_found,
            'conf_expansion': trend_confirmation_found,
            'status': status,
            'prevTR': round(prevTR, 2),
            'prevTime': previous_bar_in['time'],
            'absHighDiff': round(absHighDiff, 2),
            'absLowDiff': round(absLowDiff, 2),
            'lastTime': last_bar_in['time'],
        }

        return expansion_info

    def find_last_candle_close(first_bar_out, mode_price, expansion_info):
        nonlocal trend_confirmation_found

        if first_bar_out['low'] > mode_price:
            expansion_info['status'] = 'bull'
            trend_confirmation_found = True
            expansion_info['conf_mode'] = trend_confirmation_found
            expansion_info['conf_last_candle_close'] = trend_confirmation_found
            expansion_info['last_candle_close_mark'] = f'{first_bar_out['low']} > {mode_price}'
        elif first_bar_out['high'] < mode_price:
            expansion_info['status'] = 'bear'
            trend_confirmation_found = True
            expansion_info['conf_mode'] = trend_confirmation_found
            expansion_info['conf_last_candle_close'] = trend_confirmation_found
            expansion_info['last_candle_close_mark'] = f'{first_bar_out['high']} < {mode_price}'
        else:
            expansion_info['conf_last_candle_close'] = False
            expansion_info['last_candle_close_mark'] = f'{mode_price}'

        expansion_info['last_candle_close_time'] = first_bar_out['time']

        return expansion_info

    trend_confirmation_info = find_expansion(previous_bar_in, last_bar_in)
    if not trend_confirmation_found:
        if first_bar_out:
            trend_confirmation_info = find_last_candle_close(first_bar_out, mode_price, trend_confirmation_info)

    return trend_confirmation_info


def time_mode_find_mode_projection(mode_info, data):
    target_price_1, target_price_2, target_price_3, mode_expiration_timestamp = 0, 0, 0, 0
    is_mode_invalidated, is_mode_expired = False, False
    target_price_1_reached, target_price_2_reached, target_price_3_reached = False, False, False

    first_bar_in_index, previous_bar_in_index, last_bar_in_index = 0, 0, 0
    for i in range(len(data) - 1, -1, -1):
        if data[i]['time'] == mode_info['time_end']:
            last_bar_in_index = i
            previous_bar_in_index = i - 1
        if data[i]['time'] == mode_info['time_start']:
            first_bar_in_index = i

    mode_price = mode_info['value_start']

    # FIND MODE TR and Expiration
    if mode_info['mode_confirmation_info']['conf_expansion']:
        stop_search_index = previous_bar_in_index
    else:
        stop_search_index = last_bar_in_index

    lowest_low, highest_high = 0, 0
    for i in range(first_bar_in_index, stop_search_index + 1):
        if i == first_bar_in_index:
            lowest_low = data[i]['low']
            highest_high = data[i]['high']
        else:
            if data[i]['low'] < lowest_low:
                lowest_low = data[i]['low']
            if data[i]['high'] > highest_high:
                highest_high = data[i]['high']

    mode_tr = highest_high - lowest_low
    mode_expiration_timestamp = data[stop_search_index]['time'] + (
            data[stop_search_index]['time'] - data[first_bar_in_index]['time'])

    # FIND PRICE TARGET
    if mode_info['mode_confirmation_info']['status'] == 'bull':
        target_price_1 = mode_price + mode_tr
        target_price_2 = target_price_1 + mode_tr
        target_price_3 = target_price_2 + mode_tr

    elif mode_info['mode_confirmation_info']['status'] == 'bear':
        target_price_1 = mode_price - mode_tr
        target_price_2 = target_price_1 - mode_tr
        target_price_3 = target_price_2 - mode_tr

    # check if mode is expired
    for i in range(len(data) - 1, stop_search_index, -1):
        if data[i]['time'] == mode_expiration_timestamp:
            is_mode_expired = True
            break

    # check if mode is invalidated
    for i in range(len(data) - 1, stop_search_index + 1, -1):
        if data[i]['low'] < mode_price < data[i]['high']:
            is_mode_invalidated = True
            break

    # check if target prices reached
    for i in range(len(data) - 1, stop_search_index + 1, -1):

        if data[i]['low'] <= target_price_1 <= data[i]['high']:
            target_price_1_reached = True
        if data[i]['low'] <= target_price_2 <= data[i]['high']:
            target_price_2_reached = True
        if data[i]['low'] <= target_price_3 <= data[i]['high']:
            target_price_3_reached = True

    mode_projection_info = {
        'expiration': mode_expiration_timestamp,
        'mode_invalidated': is_mode_invalidated,
        'mode_expired': is_mode_expired,
        'target_price_1': target_price_1,
        'target_price_1_reached': target_price_1_reached,
        'target_price_2': target_price_2,
        'target_price_2_reached': target_price_2_reached,
        'target_price_3': target_price_3,
        'target_price_3_reached': target_price_3_reached,
    }

    return mode_projection_info


def filter_same_mode_price(modes_info):
    # Step 1: Identify duplicates by value_start and keep the one with the larger duration
    seen = {}
    for i, entry in enumerate(modes_info):
        if "value_start" in entry:
            value_start = entry["value_start"]
            duration = entry["time_end"] - entry["time_start"]

            # If value_start already exists, compare durations
            if value_start in seen:
                if duration > seen[value_start]["duration"]:
                    # Replace the previous entry index with the current one
                    modes_info[seen[value_start]["index"]] = None
                    seen[value_start] = {"index": i, "duration": duration}
                else:
                    # Remove the current entry
                    modes_info[i] = None
            else:
                # Store the index and duration
                seen[value_start] = {"index": i, "duration": duration}

    # Step 2: Remove `None` entries while keeping the rest intact
    modes_info = [entry for entry in modes_info if entry is not None]

    return modes_info

def filter_same_start_timestamp(modes_info):
    seen = {}  # Dictionary to track time_start and the best entry index
    result = modes_info[:]  # Create a copy to avoid modifying the original list during iteration

    for i, entry in enumerate(modes_info):
        if "time_start" in entry and "time_end" in entry:
            time_start = entry["time_start"]
            time_end = entry["time_end"]

            # If the time_start already exists in seen, compare durations
            if time_start in seen:
                existing_index = seen[time_start]["index"]
                existing_time_end = seen[time_start]["time_end"]

                if time_end > existing_time_end:
                    # Replace the previous record with None and update seen
                    result[existing_index] = None
                    seen[time_start] = {"index": i, "time_end": time_end}
                elif time_end <= existing_time_end:
                    # Mark the current entry as None, keep the first one
                    result[i] = None
            else:
                # Store the index and time_end for this time_start
                seen[time_start] = {"index": i, "time_end": time_end}

    # Remove `None` entries from the result
    filtered_result = [entry for entry in result if entry is not None]

    return filtered_result



def filter_closest_mode(closest_mode_info):
    if closest_mode_info['LL']['time_end'] > closest_mode_info['HH']['time_end']:
        closest_mode_info['HH'] = {'mode_setup_valid': False}
    elif closest_mode_info['LL']['time_end'] < closest_mode_info['HH']['time_end']:
        closest_mode_info['LL'] = {'mode_setup_valid': False}
    elif closest_mode_info['LL']['time_end'] == closest_mode_info['HH']['time_end']:
        if closest_mode_info['LL']['time_start'] > closest_mode_info['HH']['time_start']:
            closest_mode_info['LL'] = {'mode_setup_valid': False}
        elif closest_mode_info['LL']['time_start'] < closest_mode_info['HH']['time_start']:
            closest_mode_info['HH'] = {'mode_setup_valid': False}
        elif closest_mode_info['LL']['time_start'] == closest_mode_info['HH']['time_start']:
            closest_mode_info['LL'] = {'mode_setup_valid': False}

    return closest_mode_info