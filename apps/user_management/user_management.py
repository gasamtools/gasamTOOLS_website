import os
from flask import render_template_string

available_roles = ['admin', 'manager', 'contributor', 'subscriber', None]


def register_subpages(current_user):
    app_subpages = []
    return app_subpages


def app_logic(current_user, db, User, GasamApp, page, return_data):
    available_apps = GasamApp.query.all()

    if return_data:
        pass

    if page == 'user_management':
        users = User.query.all()
        send_data = {'user_data': [{'id': user.id,
                                    'user_apps': user.apps,
                                    'email': user.email,
                                    'name': user.name,
                                    'role': user.role,
                                    'approved': user.approved,
                                    'delete_user': ''
                                    } for user in users],
                     'user_roles': available_roles,
                     'available_apps': available_apps,
                     }
    else:
        send_data = {}

    return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'update_form':
        return js_function_update_form(current_user, db, User, GasamApp, json_data)


def js_function_update_form(current_user, db, User, GasamApp, json_data):
    user_to_update = User.query.get(int(json_data['user_id']))  # Get user with id=2
    if user_to_update:
        if json_data['target'] == 'approved':
            if json_data['status'] == 'approve':
                user_to_update.approved = True
                json_data['status'] = 'disapprove'
                json_data['response'] = 'True'
            elif json_data['status'] == 'disapprove':
                user_to_update.approved = False
                json_data['status'] = 'approve'
                json_data['response'] = 'False'
        if json_data['target'] == 'name':
            user_to_update.name = json_data['name']
        if json_data['target'] == 'email':
            user_to_update.email = json_data['email']
        if json_data['target'] == 'role':
            user_to_update.role = json_data['role']
        if json_data['target'] == 'delete_user':
            if user_to_update:
                db.session.delete(user_to_update)

        if json_data['target'] == 'user_apps':
            if 'user_apps_available' in json_data:
                if json_data['user_apps_available'] != '':
                    app_to_update = GasamApp.query.get(int(json_data['user_apps_available']))
                    user_to_update.apps.append(app_to_update)
            if 'user_apps_added' in json_data:
                app_to_update = GasamApp.query.get(int(json_data['user_apps_added']))
                user_to_update.apps.remove(app_to_update)
            json_data['user_apps'] = [{'id': app.id, 'app_url': app.app_url, 'app_title': app.title} for app in
                                      user_to_update.apps]

            part_html_file_path = os.path.join('apps', 'user_management', 'parts',
                                               'user_management__user_apps_list.html')
            with open(part_html_file_path, 'r') as file:
                part_html_file = file.read()

            rendered_part_html_content = render_template_string(part_html_file, user_apps=json_data['user_apps'])
            json_data['user_apps_html'] = rendered_part_html_content

        db.session.commit()  # Commit the changes to the database

    send_json_data = json_data

    return send_json_data
