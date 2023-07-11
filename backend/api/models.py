from django.db import models

from .firebase_config import *

def get_GMJI_data_firebase(name):
    lst = []
    store = []
    print(name)
    for data in dbs.child(name).child('traces').get():
        store.append(data)
         
    for datas in store:
        if datas['station'] == "GMJI":
            lst.append(datas)
    return lst

def get_JAGI_data_firebase(name):
    lst = []
    store = []
    for data in dbs.child(name).child('traces').get():
        store.append(data)     
           
    for datas in store:
        if datas['station'] == "JAGI":
            lst.append(datas)
    return lst

def get_PWJI_data_firebase(name):
    lst = []
    store = []
    for data in dbs.child(name).child('traces').get():
        store.append(data)
        
    for datas in store:
        if datas['station'] == "PWJI":
            lst.append(datas)
    return lst

