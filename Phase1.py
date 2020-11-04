'''
-*- coding: UTF-8 -*-

@author: Tianchen Luo
Note: pip install rsa
TODO: create json file for each client
'''
import rsa
import uuid
from numpy.random import seed
seed(1)

# path to store the keys(public and private) file
key_path = 'keys/'

'''
Class of client
It will generate unique id and public_key automatically
'''
class client:

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = str(first_name + ' ' + last_name)
        self.id = self.generate_unique_id()
        self.keys = self.generate_key(first_name,last_name)
        self.public_key = self.keys[0]
        self.private_key = self.keys[1]

    def generate_unique_id(self):
        id = uuid.uuid1()
        return id

    def generate_key(self,first_name, last_name):
        name = str(first_name + '_' + last_name + '_')
        (pubkey, privkey) = rsa.newkeys(1024)

        pub = pubkey.save_pkcs1()
        pubfile = open(key_path + str(name) + 'public.pem', 'wb')
        pubfile.write((pub))
        pubfile.close()

        pri = privkey.save_pkcs1()
        prifile = open(key_path + str(name) + 'private.pem', 'wb')
        prifile.write((pri))
        prifile.close()

        # public key: convert from bytes to str  original .pem file can be found under keys
        pubk = str((pub.split(b'\n')[1]+pub.split(b'\n')[2]+pub.split(b'\n')[3]),encoding = "utf-8")

        # private key
        prik = str((pri.split(b'\n')[1]+pri.split(b'\n')[2]+pri.split(b'\n')[3]+pri.split(b'\n')[4]+pri.split(b'\n')[5]+pri.split(b'\n')[6]+pri.split(b'\n')[7]+pri.split(b'\n')[8]+pri.split(b'\n')[9]+pri.split(b'\n')[10]+pri.split(b'\n')[11]+pri.split(b'\n')[12]+pri.split(b'\n')[13]),encoding = "utf-8")

        # includes both keys
        keys =[pubk,prik]
        return keys


# method to create full path
def create_full_keys_path(label):
    full_path = key_path + str(label) + 'public.pem'
    return full_path


# method to get private key
def get_private_key(label):
    path = create_full_keys_path(label)
    with open(str(path)) as privatefile:
        p = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(p)
        return privkey


# method to get public key
def get_public_key(label):
    path = create_full_keys_path(label)
    with open(str(path)) as publickfile:
        p = publickfile.read()
        pubkey = rsa.PublicKey.load_pkcs1(p)
        return pubkey


if __name__ == '__main__':
    #initialize a client
    c1 = client('Tianchen','Luo')
    print('Client --' + c1.full_name + '-- first_name is: ', c1.first_name)
    print('Client --' + c1.full_name + '-- last_name is: ', c1.last_name)
    print('Client --' + c1.full_name + '-- ID is: ',c1.id)
    print('Client --' + c1.full_name + '-- public key is: ', c1.public_key)
    print('Client --' + c1.full_name + '-- private key is: ', c1.private_key)

