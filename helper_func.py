import csv


csv_file_path='users.csv'


def check_user_id_exists(user_id):
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == str(user_id):
                    return True  
        return False  

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False 
    
async def get_email_by_user_id(user_id):
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == str(user_id):
                    return row['email']

        return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None  # Return None in case of any error
async def get_email_csv(csv_file, user_id):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['user_id'] == str(user_id):
                return row['email']
    return None

