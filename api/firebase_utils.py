import json
import os

import firebase_admin#https://firebase.google.com/docs/database/admin/start
from firebase_admin import credentials
from firebase_admin import db

from .util import get_current_meal, get_irvine_time

cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_ADMIN_CREDENTIALS")))

firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
})

def get_db_reference(location: str, meal: int, date: str) -> db.Reference:
    if meal is None:
        meal = get_current_meal()

    if date is None:
        irvine_time = get_irvine_time()
        date = f"{irvine_time.tm_mon}/{irvine_time.tm_mday}/{irvine_time.tm_year}"

    modified_datestring = date.replace("/","|")
    
    # .get() returns None if nothing created
    return db.reference(f"{location}/{modified_datestring}/{meal}")

def updateAnalytics(error=False) -> None:
    ref = db.reference("analytics")
    dbdata = ref.get()
    ref.update({'visitcount': dbdata["visitcount"] + 1})
    if error:
        ref.update({'errorcount': dbdata["errorcount"] + 1})
    return None