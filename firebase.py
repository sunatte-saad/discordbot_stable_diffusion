import firebase_admin
from firebase_admin import credentials,firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred=credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection("users")
docs = users_ref.stream()

#for doc in docs:
#    doc.to_dict()['credits']
#    print(f"{doc.id} => {doc.to_dict()}")
#    print (doc.to_dict()['credits'])


#for doc in docs:
#    id=doc.id
#    credits=doc.to_dict()['credits'] 
#    email=doc.to_dict()['email']
#    print(id,credits,email)
async def update_credits_email(email, credits):
    try:
        query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
        user_docs = query.stream()

        for user_doc in user_docs:
            user_ref = users_ref.document(user_doc.id)
            user_ref.update({'credits': credits})

            # Return the updated credits after the update
            updated_credits = user_ref.get().to_dict()['credits']
            return int(updated_credits)

        return "User not found with the provided email"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None  
def update_credits(id,credits):
    db.collection('users').document(id).update({'credits':credits})
    return ("Credits have been updated")
#update_credits(id='EpAUWKa4LggYgfHI0D6P0Gs3gYj1',credits=10)

def get_credits(id):
    credits=db.collection('users').document(id).get().to_dict()['credits']
    return (credits)
async def get_credits_email(email):
    query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
    result = query.stream()

    for doc in result:
        user_ref = users_ref.document(doc.id)
        credits = user_ref.get().to_dict()['credits']
        return int(credits)

    return "Email not found"
def check_email(email):
    query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
    result = query.stream()

    return len(list(result)) > 0

async def reduce_credits_by_one(email):
    try:
        query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
        result = query.stream()

        for doc in result:
            user_ref = users_ref.document(doc.id)
            current_credits = user_ref.get().to_dict()['credits']

            # Reduce credits by one
            updated_credits = max(0, current_credits - 1)

            user_ref.update({'credits': updated_credits})
            return int(updated_credits)

        return "Email not found"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None  # Return None in case of any error


print(update_credits_email('hifsareccoontech@gmail.com',5000))
#print (get_credits_email('raccoonsaad@gmail.com'))

#check_email('raccoonsaad@gmail.com')
    
