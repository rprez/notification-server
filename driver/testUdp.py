#!/usr/bin/python3
from uteUdpNotificationReceiver import UteUdpReceiver
import queue
import threading
import json


queue=queue.Queue()
lock=threading.Lock()


testPort=12345
udpRx = UteUdpReceiver(testPort,queue,lock)
udpRx.daemon=True
udpRx.start()

while True:
    pass