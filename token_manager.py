
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, firestore
from dotenv import load_dotenv
from os import environ
import requests

load_dotenv()

class Token:

    def __init__(self):
        if not firebase_admin._apps:

            firebase_credentials = {
                "type": environ.get('TYPE'),
                "project_id": environ.get('PROJECT_ID'),
                "private_key_id": environ.get('PRIVATE_KEY_ID'),
                "private_key": environ.get('PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": environ.get('CLIENT_EMAIL'),
                "client_id": environ.get('CLIENT_ID'),
                "auth_uri": environ.get('AUTH_URI'),
                "token_uri": environ.get('TOKEN_URI'),
                "auth_provider_x509_cert_url": environ.get('AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": environ.get('CLIENT_X509_CERT_URL'),
                "universe_domain": environ.get('UNIVERSE_DOMAIN')
            }
             
            cred = credentials.Certificate(firebase_credentials)
            firebase_admin.initialize_app(cred)
            
        self.db = firestore.client()
    
    def get_token(self):
        if self.token_is_not_valid():
            self.update_token_in_db()
        
        return self.token

    def retrieve_token_from_db(self):
        doc_ref = self.db.collection("Token").document('token')
        token = doc_ref.get()
        if token.exists:
            self.token = token.to_dict()['token']
        return self.token

    def token_is_not_valid(self):

        self.retrieve_token_from_db()

        url = f"{environ.get('APIGW_URL')}{environ.get('CHECK_TOKEN_ENDPOINT')}"

        payload = ""
        headers = {
        'Content-Type': 'application/json',
        'x-hotelid': environ.get("HOTEL_CHECK_ENDPOINT"),
        'x-app-key': environ.get("APP_KEY"),
        'Authorization': f'Bearer {self.token}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            return False
        else:
            return True


    def update_token_in_db(self):

        url = f"{environ.get('APIGW_URL')}/oauth/v1/tokens"

        payload = f'username={environ.get('INTEGRATION_USER')}&password={environ.get('INTEGRATION_PASSWORD')}&grant_type=password'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-app-key': environ.get("APP_KEY"),
        'Authorization': f'Basic {environ.get("BASIC_AUTH")}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            self.token = response.json()['access_token']
        else:
            raise ValueError("Erro ao obter novo JWT da API.")
        
        self.db = firestore.client()

        token = self.db.collection("Token").document("token")
        token.update({"isValid": True, "token": self.token})
        self.retrieve_token_from_db()
