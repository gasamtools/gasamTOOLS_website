# app1 = GasamApp(title="User Management", subtitle="For admin only", app_url="user_management")
# current_user.apps.append(app1)
# current_user.approved = True
# current_user.role = 'admin'
# db.session.commit()

def app_logic(current_user, db, User, GasamApp, return_data):
    send_data = {'test':'works'}

    return send_data