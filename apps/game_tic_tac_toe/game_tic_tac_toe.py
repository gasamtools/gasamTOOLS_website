import random
import os
import re
from typing import List, Any

GAME_TIC_TAC_TOE_AI_PLAYS = False
GAME_TIC_TAC_TOE_AI_TEAM: str

GAME_TIC_TAC_TOE_PLAYER_MOVE = 'cross'
GAME_TIC_TAC_TOE_WINNING_COMBOS = [
    [[1, 2, 3], 'crossing-1'],
    [[4, 5, 6], 'crossing-2'],
    [[7, 8, 9], 'crossing-3'],
    [[1, 4, 7], 'crossing-4'],
    [[2, 5, 8], 'crossing-5'],
    [[3, 6, 9], 'crossing-6'],
    [[1, 5, 9], 'crossing-7'],
    [[3, 5, 7], 'crossing-8'],

]

GAME_TIC_TAC_TOE_PLAYER_CROSS = []
GAME_TIC_TAC_TOE_PLAYER_CIRCLE = []


def register_subpages():
    app_subpages = [
    ]

    return app_subpages


def register_database(db, app):
    pass


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'game_tic_tac_toe':
        global GAME_TIC_TAC_TOE_PLAYER_CROSS, GAME_TIC_TAC_TOE_PLAYER_CIRCLE
        global GAME_TIC_TAC_TOE_PLAYER_MOVE, GAME_TIC_TAC_TOE_AI_PLAYS

        GAME_TIC_TAC_TOE_PLAYER_MOVE = 'cross'
        GAME_TIC_TAC_TOE_AI_PLAYS = False
        GAME_TIC_TAC_TOE_PLAYER_CROSS = []
        GAME_TIC_TAC_TOE_PLAYER_CIRCLE = []
        file_path_coin_gif_choice_undecided = os.path.join('apps', 'game_tic_tac_toe', 'static', 'choice_undecided.gif')
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

    return send_data


def json_logic(current_user, db, User, GasamApp, json_data):
    if json_data['js_function'] == 'game_tic_tac_toe_choose_ai':
        return js_function_game_tic_tac_toe_choose_ai(current_user, db, User, GasamApp, json_data)
    if json_data['js_function'] == 'game_tic_tac_toe_game_engine':
        return js_function_game_tic_tac_toe_game_engine(current_user, db, User, GasamApp, json_data)
    if json_data['js_function'] == 'game_tic_tac_toe_game_engine_reset':
        return js_function_game_tic_tac_toe_game_engine_reset(current_user, db, User, GasamApp, json_data)


def js_function_game_tic_tac_toe_choose_ai(current_user, db, User, GasamApp, json_data):
    global GAME_TIC_TAC_TOE_AI_PLAYS, GAME_TIC_TAC_TOE_AI_TEAM

    user_coin_choice = json_data['coin_choice']
    random_choice = random.randint(0, 1)
    if random_choice == 0:
        random_coin_choice = 'heads'
    else:
        random_coin_choice = 'tails'

    if user_coin_choice == random_coin_choice:
        json_data['user_choice_status'] = True
        GAME_TIC_TAC_TOE_AI_TEAM = 'circle'
    else:
        json_data['user_choice_status'] = False
        GAME_TIC_TAC_TOE_AI_TEAM = 'cross'

    GAME_TIC_TAC_TOE_AI_PLAYS = True
    json_data['ai_move'] = js_function_game_tic_tac_toe_game_ai_engine()
    json_data['player_move'] = GAME_TIC_TAC_TOE_PLAYER_MOVE

    return json_data


def js_function_game_tic_tac_toe_game_engine(current_user, db, User, GasamApp, json_data):
    global GAME_TIC_TAC_TOE_PLAYER_MOVE
    json_data['player_move'] = GAME_TIC_TAC_TOE_PLAYER_MOVE

    square_clicked = json_data['square_clicked']
    square_clicked_numbers = re.findall(r'\d+', square_clicked)
    square_clicked_number = square_clicked_numbers[0]

    if GAME_TIC_TAC_TOE_PLAYER_MOVE == 'cross':

        GAME_TIC_TAC_TOE_PLAYER_CROSS.append(int(square_clicked_number))
        GAME_TIC_TAC_TOE_PLAYER_MOVE = 'circle'

    elif GAME_TIC_TAC_TOE_PLAYER_MOVE == 'circle':

        GAME_TIC_TAC_TOE_PLAYER_CIRCLE.append(int(square_clicked_number))
        GAME_TIC_TAC_TOE_PLAYER_MOVE = 'cross'

    json_data['ai_plays'] = GAME_TIC_TAC_TOE_AI_PLAYS

    js_function_game_tic_tac_toe_game_check_if_winner(json_data)

    if GAME_TIC_TAC_TOE_AI_PLAYS and 'winner' in json_data:
        json_data['ai_plays'] = False

    if GAME_TIC_TAC_TOE_AI_PLAYS and 'winner' not in json_data:
        json_data['ai_move'] = js_function_game_tic_tac_toe_game_ai_engine()
        js_function_game_tic_tac_toe_game_check_if_winner(json_data)

    return json_data


def js_function_game_tic_tac_toe_game_engine_reset(current_user, db, User, GasamApp, json_data):
    global GAME_TIC_TAC_TOE_PLAYER_CROSS, GAME_TIC_TAC_TOE_PLAYER_CIRCLE
    global GAME_TIC_TAC_TOE_AI_PLAYS, GAME_TIC_TAC_TOE_PLAYER_MOVE

    GAME_TIC_TAC_TOE_PLAYER_MOVE = 'cross'
    GAME_TIC_TAC_TOE_PLAYER_CROSS = []
    GAME_TIC_TAC_TOE_PLAYER_CIRCLE = []
    GAME_TIC_TAC_TOE_AI_PLAYS = False

    return json_data


def js_function_game_tic_tac_toe_game_ai_engine():
    move: int

    global GAME_TIC_TAC_TOE_PLAYER_CROSS, GAME_TIC_TAC_TOE_PLAYER_CIRCLE
    global GAME_TIC_TAC_TOE_AI_TEAM, GAME_TIC_TAC_TOE_PLAYER_MOVE

    if GAME_TIC_TAC_TOE_PLAYER_MOVE == GAME_TIC_TAC_TOE_AI_TEAM:
        all_moves = list(range(1, 10))
        all_moves = [x for x in all_moves if x not in GAME_TIC_TAC_TOE_PLAYER_CROSS]
        all_moves = [x for x in all_moves if x not in GAME_TIC_TAC_TOE_PLAYER_CIRCLE]

        circle_almost_win  = 0
        cross_almost_win = 0
        for combo in GAME_TIC_TAC_TOE_WINNING_COMBOS:
            circle_count = sum(1 for elem in combo[0] if elem in GAME_TIC_TAC_TOE_PLAYER_CIRCLE)
            if circle_count >= 2:
                circle_almost_win_arr = [x for x in combo[0] if x not in GAME_TIC_TAC_TOE_PLAYER_CIRCLE]
                if circle_almost_win_arr[0] not in GAME_TIC_TAC_TOE_PLAYER_CROSS:
                    circle_almost_win = circle_almost_win_arr[0]

            cross_count = sum(1 for elem in combo[0] if elem in GAME_TIC_TAC_TOE_PLAYER_CROSS)
            if cross_count >= 2:
                cross_almost_win_arr = [x for x in combo[0] if x not in GAME_TIC_TAC_TOE_PLAYER_CROSS]
                if cross_almost_win_arr[0] not in GAME_TIC_TAC_TOE_PLAYER_CIRCLE:
                    cross_almost_win = cross_almost_win_arr[0]

        # check if position 5 is available
        if 5 not in GAME_TIC_TAC_TOE_PLAYER_CROSS and 5 not in GAME_TIC_TAC_TOE_PLAYER_CIRCLE:
            move = 5

        # check if ai is almost winning and finish
        elif GAME_TIC_TAC_TOE_AI_TEAM == 'cross' and cross_almost_win != 0:
            move = cross_almost_win

        elif GAME_TIC_TAC_TOE_AI_TEAM == 'circle' and circle_almost_win != 0:
            move = circle_almost_win

        # check if opponent is almost winning and block
        elif GAME_TIC_TAC_TOE_AI_TEAM == 'circle' and cross_almost_win != 0:
                move = cross_almost_win

        elif GAME_TIC_TAC_TOE_AI_TEAM == 'cross' and circle_almost_win != 0:
                move = circle_almost_win

        # pick a random move
        else:
            move = random.choice(all_moves)


        if GAME_TIC_TAC_TOE_AI_TEAM == 'cross':
            GAME_TIC_TAC_TOE_PLAYER_CROSS.append(move)
            GAME_TIC_TAC_TOE_PLAYER_MOVE = 'circle'
        elif GAME_TIC_TAC_TOE_AI_TEAM == 'circle':
            GAME_TIC_TAC_TOE_PLAYER_CIRCLE.append(move)
            GAME_TIC_TAC_TOE_PLAYER_MOVE = 'cross'

        return move
    else:
        return False

def js_function_game_tic_tac_toe_game_check_if_winner(json_data):
    global GAME_TIC_TAC_TOE_WINNING_COMBOS, GAME_TIC_TAC_TOE_PLAYER_CIRCLE, GAME_TIC_TAC_TOE_PLAYER_CROSS

    for combo in GAME_TIC_TAC_TOE_WINNING_COMBOS:
        if all(elem in GAME_TIC_TAC_TOE_PLAYER_CIRCLE for elem in combo[0]):
            json_data['winner'] = 'circle'
            json_data['winner_strike'] = combo[1]
        if all(elem in GAME_TIC_TAC_TOE_PLAYER_CROSS for elem in combo[0]):
            json_data['winner'] = 'cross'
            json_data['winner_strike'] = combo[1]

    moves_made = len(GAME_TIC_TAC_TOE_PLAYER_CIRCLE) + len(GAME_TIC_TAC_TOE_PLAYER_CROSS)
    if moves_made == 9 and 'winner' not in json_data:
        json_data['winner'] = 'none'

    return json_data
