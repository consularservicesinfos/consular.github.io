import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GMAIL_USER = os.getenv('GMAIL_USER', 'consular.services.infos@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'Adam23031979*')
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre_cle_secrete_api_2024')