import json
import codecs

"""
@author: Tianchen
Initialise the client class includes information of: id, name, pubkey, prikey
"""
class Client:

    def __init__(self, json_name):
        self.id = self.get_id(json_name)
        self.name = self.get_name(json_name)
        self.pubkey = self.get_pubkey(json_name)
        self.prikey = self.get_prikey(json_name)

    @staticmethod
    def get_id(json_name):
        with codecs.open('json_files/' + json_name+'.json', 'r+', encoding='utf8') as users_file:
            data = json.load(users_file)
            user_id = data["person"]["id"]
        return user_id

    @staticmethod
    def get_name(json_name):
        with codecs.open('json_files/' + json_name + '.json', 'r+', encoding='utf8') as users_file:
            data = json.load(users_file)
            user_name = data["person"]["name"]
        return user_name

    @staticmethod
    def get_pubkey(json_name):
        with codecs.open('json_files/' + json_name + '.json', 'r+', encoding='utf8') as users_file:
            data = json.load(users_file)
            user_pubkey = data["person"]["keys"]["public"]
        return user_pubkey

    @staticmethod
    def get_prikey(json_name):
        with codecs.open('json_files/' + json_name + '.json', 'r+', encoding='utf8') as users_file:
            data = json.load(users_file)
            user_prikey = data["person"]["keys"]["private"]
        return user_prikey


if __name__ == '__main__':
    kk = Client('config_1')
    print(kk.id)
    print(kk.pubkey)
    print(kk.name)
    print(kk.prikey)