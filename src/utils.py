import os

def empty_queue(q):
    while not q.empty():
        q.get()

def reboot():
    os.system('sudo shutdown -r now')