#This script reads an excel file that lists IP addresses under the heading "IP" and prints as much information as it recieves from each miner to the console using the data received via pycgminer API.
#Written by Katie Gronemann

import socket
import json
import sys
from requests.auth import HTTPDigestAuth
from pycgminer import CgminerAPI
import pandas as pd
import os

if __name__ == '__main__':
    global gldf
    global counter
    counter = 0
    # Test for IPlist 
    if os.path.isfile('IPList.xls'):
        gldf = pd.read_excel('IPList.xls')
    else:
        print('File does not exist. Please create file "IPList.xls" and then try to run this program.')
        sys.exit(0)
        
    for i in range(len(gldf.index)):
        host = gldf.at[i, 'IP']
    
        try:
            Miner = CgminerAPI(host)
            data = Miner.stats()
            hr = float(data['STATS'][1]['GHS 5s'])
            if hr < 100:
                fans = [0,0,0,0]
                print (f"\nHashrate: {hr}")
                for i in range(len(fans)):
                    try:
                        fans[i]=data['STATS'][1][f'fan{i+1}']
                    except KeyError as e:
                        print (f"fan{i+1} not found")
                        fans[i] = 0
                print(host + ": " +str(fans))
                worst = 6000
                for i in range(len(fans)):
                    if (fans[i] > worst+(worst*0.15) or fans[1] < worst-(worst*0.15)):
                        print (f"dead fan: fan {i+1}")
        except KeyError as e:
            print ("Key error: " + e)

        

   
 


