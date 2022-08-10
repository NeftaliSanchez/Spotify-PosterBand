from credentials import credentials
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from urllib.parse import urlencode
from datetime import datetime, timezone
import platform
import requests
import base64
import time
import os
import re
import json
import webbrowser

# take a look to get more information
# https://developer.spotify.com/documentation/general/guides/authorization/code-flow/

## OS
plataform_system = platform.system()

# get client id and secret key from credentials
client_id = credentials.obtain('id')
client_secret = credentials.obtain('secret')

### Authorization Code Flow ####
# Request User Authorization ()
auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "https://www.google.com.mx/",
    "scope": "user-top-read user-read-private user-read-recently-played"
}
link = "https://accounts.spotify.com/authorize?" + urlencode(auth_headers)

seleccion = input(''' Proceder con: 
    1   Selenium
    2   Webbrowser
    
seleccion: ''')
#### with SELENIUM
if seleccion == '1':
# For webbroser (login)
    driver =  webdriver.Chrome(executable_path=r".\chromedriver_win32\chromedriver.exe")
    driver.get(link)
    ## to keeping opened selenuim until user login in 
    poll_rate = 1
    while True:
        time.sleep(poll_rate)
        time.sleep(2)
        current =  driver.current_url
        valid_url_spotify = re.search('accounts.spotify.com/',current)
        valid_url_facebook = re.search('www.facebook.com/',current)
        if valid_url_spotify is None and valid_url_facebook is None: break
    driver.quit()
    code = str(current)
#### whith webbrowser
elif seleccion == '2':
    webbrowser.open_new(link)
    code = input('ingresa la url: ')
else: quit()

# get the code key
token_code = re.findall('code=(.*)#_=_$',code)
if len(token_code) == 0 : token_code = re.findall('code=(.*)',code)
token_code = token_code[0]

######################################
# clear screen
try:
    if plataform_system == 'Linux': os.system('clear')
    elif plataform_system == 'Windows':os. system('cls')
except: pass
######################################

### Authorization Code Flow ####
# Request Access Token ()
client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())
token_url = "https://accounts.spotify.com/api/token"
method = "POST"
token_data = {
    "grant_type": "authorization_code",
    "code": token_code,
    "redirect_uri": "https://www.google.com.mx/"
}
token_header = {
    "Authorization": f"Basic {client_creds_b64.decode()}",
    "Content-Type": "application/x-www-form-urlencoded"
}
r =  requests.post(token_url,data=token_data,headers=token_header)

# Response from the spotify API (<Response [200]> == OK)
# print(r)
token = r.json()["access_token"]

##################################################################################
print('''
    1   info user
    2   top tracks
    3   recently played
''')
type_request = input("enter id: ")

###### get info profile
if type_request == '1':
    requests_url = 'https://api.spotify.com/v1/me/'
    user_header = {
        "Authorization": f"Bearer {token}",
        "Content-Type" : "application/json"
    }
    user_tracks_response = requests.get(requests_url,headers=user_header)
    # Response from the spotify API
    # print(user_tracks_response)
    try: json_data = user_tracks_response.json()
    except: 
        print("error") 
        quit()
    # print json
    json_formatted_str = json.dumps(json_data, indent=2)
    print(json_formatted_str)

###### Get the current user's top tracks based on calculated affinity.
elif type_request == '2':
    while True:
        try: limit = int(input('Limite de busqueda (máximo 50): '))
        except:
            print('Entrada invalida')
            continue
        if limit >= 1 and limit <= 50: break
        else: print('Entrada invalida')
    requests_url = f'https://api.spotify.com/v1/me/top/tracks?limit={limit}'
    user_header = {
        "Authorization": f"Bearer {token}",
        "Content-Type" : "application/json"
    }
    user_tracks_response = requests.get(requests_url,headers=user_header)
    # Response from the spotify API
    # print(user_tracks_response)
    try: json_data = user_tracks_response.json()
    except: 
        print("error") 
        quit()
    for i in range(0,limit):
        print('----------------------------------------------')
        print(f'Número {i+1}') 
        try:
            artists = list()
            j = 0
            while True:
                Artista = json_data["items"][i]["artists"][0]["name"]
                if Artista in artists: break
                artists.append(Artista)
                j=j+1
        except: pass
        artistas = None
        for artist in artists:
            if artistas is None: artistas = artist
            else: artistas = f'{artistas}, {artist}'
        print(f'Artista(s): {artistas}')
        print(f'Rola: {json_data["items"][i]["name"]}')

###### recently played 
elif type_request == '3':
    limit = 50
    #  GMT(Greenwich Mean Time)/UTC(Coordinated Universal Time)
    # Zona horaria de Mexico -> GMT-5
    date = round(datetime.now(timezone.utc).timestamp() * 1000)
    requests_url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}&before={date}'
    # requests_url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}&after={date}'
    user_header = {
        "Authorization": f"Bearer {token}",
        "Content-Type" : "application/json"
    }
    user_tracks_response = requests.get(requests_url,headers=user_header)
    print(user_tracks_response)
    try: 
        json_data = user_tracks_response.json()
        for i in range(0,limit):
            print('----------------------------------------------')
            print(f'Número {i+1}') 
            try:
                artists = list()
                j = 0
                while True:
                    Artista = json_data["items"][i]["track"]["album"]["artists"][j]["name"]
                    if Artista in artists: break
                    artists.append(Artista)
                    j=j+1
            except: pass
            artistas = None
            for artist in artists:
                if artistas is None: artistas = artist
                else: artistas = f'{artistas}, {artist}'
            print(f'Artista(s): {artistas}')
            print(f'Rola: {json_data["items"][i]["track"]["name"]}')
            # GMT hour
            date = datetime.fromisoformat((re.findall('(.*)\.[0-9]+Z$',json_data["items"][i]["played_at"]))[0])
            print(f'Fecha que se esucho: {date}')
    except: quit()
else: quit()
        