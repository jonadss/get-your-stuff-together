import maskpass
from passlib.hash import bcrypt

from argon2 import PasswordHasher


def hash_password(password):
    # Configure the algorithm
    time_cost = 2          # Number of iterations
    memory_cost = 102400   # 100 MB in KiB
    parallelism = 8        # Number of parallel threads
    hash_len = 32          # Length of the hash in bytes
    salt_len = 16          # Length of the salt in bytes
    
    # Create the hasher
    ph = argon2.PasswordHasher(
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=hash_len,
        salt_len=salt_len,
        type=argon2.Type.ID  # Using Argon2id variant
    )
    
    # Hash the password (salt is generated automatically)
    hash = ph.hash(password)
    
    return hash





ph = PasswordHasher()

user_db = {}
def createpwd():
    


    print("\n======== Create Account =========")
    name = input("Username : ")
    pwd = maskpass.askpass("Password : ")
    

    hashed_password = hash_password(pwd)

    print("Hashed password:", hashed_password)


    user_db[name] = hashed_password
    print(f"Account für {name} wurde erstellt.")

def sign_in():
    print("\n========= Login Page ===========")
    name = input("Username : ")
    
    if name not in user_db:
        print("User nicht vorhanden")
        return

    pwd = maskpass.askpass("Password : ")
    stored_hash = user_db[name]

    try:
        ph.verify(stored_hash, pwd)
        print("Password is valid!")
    except Exception:
        print("Invalid password!")


# Programmablauf
createpwd()
sign_in()