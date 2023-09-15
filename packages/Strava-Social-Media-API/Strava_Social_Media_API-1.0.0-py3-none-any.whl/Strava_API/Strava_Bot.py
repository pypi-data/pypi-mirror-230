"""
This is an example how you can use the Strava Social Media API.
It is also a place to test new methods of the Social Media API
"""

from Strava_API import Client
import json

#Using to hide my credentials
def get_my_hidden_credentials():
    
    file_path = 'D:\Dokumenti\Python\credentials.json'  
    with open(file_path, 'r') as file:
        credentials = json.load(file)
        strava_email = credentials.get('STRAVA_EMAIL')
        strava_password = credentials.get('STRAVA_PASSWORD')
    return strava_email, strava_password

def main():
    cl = Client()
    
    email,password = get_my_hidden_credentials()
    cl.login(email, password)
    
    #Tadej Pogacar's ID. See ReadMe on where to get the code
    pogacar = '6021015'
    
    cl.follow( pogacar)
    cl.unfollow(pogacar)

    print(cl.get_followers_list(pogacar))
    print( cl.get_activity_ids_from_user('37528897', 500) )
    print(cl.get_kudos_list_from_activity('9419737987') )
    
    cl.download_gpx_files(['9419737987','9790149320'], destination_directory = 'D:\Dokumenti\Python\GPX', download_directory = 'D:\Prenosi', wait_for_dowload_s = 5)
    cl.like_activity('9790149320')
    cl.comment_on_activity('9790149320', "Good job! :)")

if __name__ == "__main__":
    main()


