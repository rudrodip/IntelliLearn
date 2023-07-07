import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("intelli-learn.json")
firebase_admin.initialize_app(cred)

print('successfully initialized firebase')
db = firestore.client()

def get_user_data(uid):
    user_ref = db.collection("users").document(uid)
    user_data = user_ref.get().to_dict()
    
    if user_data:
        return user_data
    else:
        return None
    

def write_user_data(uid, field, value):
    db = firestore.client()
    user_ref = db.collection("users").document(uid)

    # Get the existing user data
    user_data = user_ref.get().to_dict()

    if user_data:
        # Update the specific field in the user data
        user_data[field] = value

        # Update the user data in Firestore
        user_ref.set(user_data)
        print(f"Successfully updated '{field}' field for user with UID {uid}")
        return True
    else:
        print(f"User with UID {uid} not found.")
        return False
    
def check_registered_user(registered_users, user_id):
    if user_id not in registered_users:
        user_data = get_user_data(user_id)
        if user_data:
            registered_users.add(user_id)
            return True
        else:
            return False
    return True