#!/usr/bin/python3
# -*- coding: utf-8 -*-

from kot import KOT, KOT_Remote, HASHES

class KOT_Secret_Controller:
    def __init__(self, encryption_key, database_name, api_url, password=None) -> None:
        self.encryption_key = encryption_key
        self.connection = KOT_Remote(database_name, api_url, password)
    def add_secret(self, secret_name, secret):
        self.connection.set(secret_name, secret, encryption_key=self.encryption_key)
    def delete_secret(self, secret_name):
        self.connection.delete(secret_name)        
    def get_secret(self, secret_name):
        return self.connection.get(secret_name, encryption_key=self.encryption_key)

def KOT_Secret(encryption_key, database_name):
    return KOT_Secret_Controller(encryption_key, database_name, "http://free.cloud.kotdatabase.dev:5000", "onuratakan")

def KOT_Secret_Pro(encryption_key, database_name, access_key):
    return KOT_Secret_Controller(encryption_key, database_name, "http://free.cloud.kotdatabase.dev:5001", access_key)

def KOT_Secret_Dedicated(encryption_key, database_name, password, dedicated_key):
    dedicated_key = dedicated_key.replace("dedicatedkey-", "")
    dedicated_key = dedicated_key.encode()
    resolver = KOT("dedicate_resolver")
    resolver.set(dedicated_key.decode(), dedicated_key)
    host = resolver.get(dedicated_key.decode(), encryption_key="dedicatedkey")
    return KOT_Secret_Controller(encryption_key, database_name, host, password)