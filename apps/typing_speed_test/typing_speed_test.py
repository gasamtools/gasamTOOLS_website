import os


def register_subpages():
    app_subpages = [
    ]
    return app_subpages


def register_database(db, app):
    pass


def app_logic(current_user, db, User, GasamApp, page, return_data):

    if page == 'typing_speed_test':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'typing_speed_test_ini':
        return js_function_typing_speed_test_ini(current_user, db, User, GasamApp, json_data, files_data)


def js_function_typing_speed_test_ini(current_user, db, User, GasamApp, json_data, files_data):
    # install plugin packages
    from main import check_and_install_requirements
    requirements_dir = os.path.join('apps', 'typing_speed_test', 'typing_speed_test_requirements.txt')
    check_and_install_requirements(requirements_dir)

    # test installed nuumpy package
    sum_val, mean_val, max_val, min_val = array_operations()
    print(f"Sum: {sum_val}, Mean: {mean_val}, Max: {max_val}, Min: {min_val}")

    return {'status': 'packages installed',
            'Sum': str(sum_val),
            'Mean': str(mean_val),
            'Max': str(max_val),
            'Min': str(min_val),
            }

def array_operations():
    import numpy as np
    # Create a NumPy array
    array = np.array([1, 2, 3, 4, 5])

    # Perform some operations
    sum_array = np.sum(array)  # Sum of all elements
    mean_array = np.mean(array)  # Mean of the array
    max_value = np.max(array)  # Maximum value in the array
    min_value = np.min(array)  # Minimum value in the array

    return sum_array, mean_array, max_value, min_value
