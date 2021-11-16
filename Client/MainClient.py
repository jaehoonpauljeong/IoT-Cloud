import threading
import os

def startIPS():
    os.system("sudo python3 SALA/BLE.py")

def startClient():
    os.system("sudo java -jar Client.jar")

thread1 = threading.Thread(target=startIPS, args=())
thread2 = threading.Thread(target=startClient, args=())

thread1.start()
thread2.start()
