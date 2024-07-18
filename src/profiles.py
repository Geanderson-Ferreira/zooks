import requests
from dotenv import load_dotenv
from os import environ
from flask import flash

load_dotenv()

def get_profiles_by_ids(profiles_ids, hotel, token):
    url = f"{environ['APIGW_URL']}/crm/v1/profilesByIds"
    params = {
        "profileIds": profiles_ids,
    }
    headers = {
    'x-hotelid': hotel,
    'x-app-key': environ['APP_KEY'],
    'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        flash(response.text)
        return False