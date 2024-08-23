available_roles = ['admin', 'manager', 'contributor', 'subscriber', None]


def app_logic(current_user, db, User, GasamApp, return_data):

    available_apps = GasamApp.query.all()

    if return_data:
        user_to_update = User.query.get(int(return_data['user_id']))  # Get user with id=2
        if user_to_update:
            if return_data['target'] == 'approved':
                if return_data['status'] == 'approve':
                    user_to_update.approved = True
                elif return_data['status'] == 'disapprove':
                    user_to_update.approved = False
            if return_data['target'] == 'name':
                user_to_update.name = return_data['name']
            if return_data['target'] == 'email':
                user_to_update.email = return_data['email']
            if return_data['target'] == 'role':
                user_to_update.role = return_data['role']
            if return_data['target'] == 'user_apps':
                if 'user_apps_available' in return_data:
                    if return_data['user_apps_available'] != '':
                        app_to_update = GasamApp.query.get(int(return_data['user_apps_available']))
                        user_to_update.apps.append(app_to_update)
                if 'user_apps_added' in return_data:
                    app_to_update = GasamApp.query.get(int(return_data['user_apps_added']))
                    user_to_update.apps.remove(app_to_update)
            db.session.commit()  # Commit the changes to the database

    users = User.query.all()
    send_data = {'user_data': [{'id': user.id,
                                'user_apps': user.apps,
                                 'email': user.email,
                                 'name': user.name,
                                 'approved': user.approved,
                                 'role': user.role,
                                } for user in users],
                  'user_roles': available_roles,
                  'available_apps': available_apps
                  }

    return send_data
