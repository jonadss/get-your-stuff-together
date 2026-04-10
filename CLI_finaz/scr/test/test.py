# Hiding the inputted password with maskpass()
# and encrypting it with use of base64()
import maskpass  # to hide the password
import base64  # to encode and decode the password

# dictionary with username
# as key & password as value
dict = {'Rahul': b'cmFodWw=',
        'Sandeep': b'U2FuZGVlcA=='}

# function to create password
def createpwd():
    print("\n========Create Account=========")
    name = input("Username : ")
    
    # masking password with prompt msg 'Password :'
    pwd = maskpass.askpass("Password : ")
    
    # encoding the entered password
    encpwd = base64.b64encode(pwd.encode("utf-8"))

    # appending username and password in dict
    dict[name] = encpwd  
    # print(dict)

# function for sign-in
def sign_in():
    print("\n\n=========Login Page===========")
    name = input("Username : ")
    
    # masking password with prompt msg 'Password :'
    pwd = maskpass.askpass("Password : ")
    
    # encoding the entered password
    encpwd = base64.b64encode(pwd.encode("utf-8"))

    # fetching password with
    # username as key in dict
    password = dict[name]  
    if(encpwd == password):
        print("Successfully logged in.")
    else:
        print("Login Failed")



createpwd()


try:
    sign_in()

except KeyError:
    print("User nicht vorhanden")