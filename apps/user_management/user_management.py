
def custom_logic(current_user, db, User, GasamApp, returned_data):

    if returned_data:
        user_to_update = User.query.get(int(returned_data['user_id']))  # Get user with id=2
        if user_to_update:
            if returned_data['status'] == 'approve':
                user_to_update.approved = True
            elif returned_data['status'] == 'disapprove':
                user_to_update.approved = False
            db.session.commit()  # Commit the changes to the database

    users = User.query.all()
    users_data = [{'id': user.id,
                   'email': user.email,
                   'name': user.name,
                   'approved': user.approved,
                   'role': user.role,
                   'user_apps': [app.app_url for app in user.apps]} for user in users]

    return users_data