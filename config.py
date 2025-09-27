import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
TO = os.getenv("TO")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
