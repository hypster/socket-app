import threading
from subprocess import call
from new_system import client_new
import time


# simple script to perform everything without needing to change terminals
def run_server():
    call(["python3", "new_system/server_new.py"])


def run_client1():
    client_new.Client("json_files/config_1.json").connect()


def run_client2():
    client_new.Client("json_files/config_2.json").connect()


# start threads
server_thread = threading.Thread(target=run_server)
server_thread.start()

time.sleep(5)

client1_thread = threading.Thread(target=run_client1)
client1_thread.start()


client2_thread = threading.Thread(target=run_client2)
client2_thread.start()
