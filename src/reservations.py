import requests
from dotenv import load_dotenv
from os import environ
from flask import flash

load_dotenv()

def get_reservations_by_ids(hotel, reservations_id_list, token):
    url = f"{environ['APIGW_URL']}/rsv/v1/hotels/{hotel}/reservations"
    headers = {
    'Content-Type': 'application/json',
    'x-hotelid': hotel,
    'x-app-key': environ['APP_KEY'],
    'Authorization': f'Bearer {token}'
    }

    all_reservations = []
    limit = 200
    offset = 0
    has_more = True

    while has_more:
        params = {
            'limit': limit,
            'offset': offset,
            "reservationIdList": reservations_id_list,
        }
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['reservations']['totalResults'] == 0:
                if len(all_reservations) > 0:
                    return all_reservations
                else:
                    return False
            
            reservations = data['reservations']['reservationInfo']
            all_reservations.extend(reservations)
            
            # Atualiza o offset e o has_more
            offset += limit
            has_more = data['reservations']['hasMore']
        else:
            flash(response.text)
            return False

    return all_reservations


def get_reservations_by_checkout_date(hotel, checkout_date, token):
    url = f"{environ['APIGW_URL']}/rsv/v1/hotels/{hotel}/reservations"
    headers = {
        'Content-Type': 'application/json',
        'x-hotelid': hotel,
        'x-app-key': environ['APP_KEY'],
        'Authorization': f'Bearer {token}'
    }
    
    all_reservations = []
    limit = 200
    offset = 0
    has_more = True
    
    while has_more:
        params = {
            'limit': limit,
            'offset': offset,
            "departureEndDate":checkout_date,
            "departureStartDate": checkout_date,
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['reservations']['totalResults'] == 0:
                if len(all_reservations) > 0:
                    return all_reservations
                else:
                    return False
            
            reservations = data['reservations']['reservationInfo']
            all_reservations.extend(reservations)
            
            # Atualiza o offset e o has_more
            offset += limit
            has_more = data['reservations']['hasMore']
        else:
            flash(response.text)
            return False
    
    return all_reservations