#This script grabs the "nonce rate" of a target miner by ip address. This works for S19 family miners, but not every firmware may be supported.
#Written by Katie Gronemann
from datetime import datetime
import os
import sys
import requests
import json
import tkinter.scrolledtext as tks
import socket
import time
import threading
from random import randint, choice
from requests.auth import HTTPDigestAuth
from pycgminer import CgminerAPI
from tkinter import *

if __name__ == '__main__':
    ip = '1.2.3.4'
    data = CgminerAPI(ip).stats()
    USR = 'root'
    PSS = 'root'
    try:
        
        nurl = f'http://{ip}:6060/nonce'
        n = requests.get(nurl, auth=HTTPDigestAuth(USR, PSS), timeout=1)
        y = n.text
        s = y.split('\n')
        print (str(s))
        for line in s:
            #s = line.split()
            if (line!=""):
                print (str(line))
                print ("what")
            #print (f"D{s[1]} {s[4]}")

    except requests.ConnectTimeout as e:
        print (f"Connection Timeout, is the VPN Connection Live? {e}")

    
