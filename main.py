#KG's 'Kick-Ass' Kernel Puller
#Written by Katie Gronemann
#This program is intended for use on a raspberry pi with a very small screen. Modifications may be required for desktop use, but it is servicable on several displays.


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
import webbrowser


def pullInfo(ip):
    global RKL
    global STS
    global ERR
    global IPA
    global IPS
    global USR
    global PSS
    global TYP
    global BNK
    global REC
    global FAN
    global ASC
    global CHN
    global BOA
    
    RKL = ""
    STS = ""
    ERR = ""
    IPA = ""
    IPS = ["","","",""]
    USR = ""
    PSS = ""
    TYP = ""
    BNK = "off"
    REC = ""
    FAN = [0,0,0,0]
    ASC = [0, 0, 0, 0]
    CHN = [0,0,0,0]
    BOA = 3

    T1.config(state=NORMAL)
    T1.delete('1.0', END)
    T2.config(state=NORMAL)
    T2.delete('1.0', END)
    T3.config(state=NORMAL)
    T3.delete('1.0', END)
    L4.config(state=NORMAL)
    L4.delete('1.0', END)
    USR=usr_var.get()
    PSS=pss_var.get()
    IPA=ip
    
    IPS = IPA.split('.')
    if len(IPS) < 4 or len(IPS) > 4:
        RKL = "Invalid IP Address Entered. You're stupid!"
        
    else:
        ret = getkl(IPA)
        prt = prints(IPA)
        RKL = ret[0]
        STS = prt[0]
        
        ERR = ret[1]
        
        TYP = ret[2]
        REC = reccomend(ret[3], prt[1].split('*'))

        if(AS.get() == 1):
            makef()             

    T1.insert(END,RKL + "\n")
    T1.see(END)
    T1.config(state=DISABLED)
    
    T2.insert(END, f"{TYP}\n{STS}\n")
    T2.config(state=DISABLED)

    T3.tag_add("main", '1.8', '1.13')
    T3.tag_add("recc", '1.8', '1.13')
    T3.tag_config("main", foreground = "black")
    T3.tag_config("recc", foreground = "red")
    
    T3.insert(END, ERR, "main")
    T3.insert(END, REC+"\n", "recc")
    T3.see(END)
    T3.config(state=DISABLED)
    L4.insert(END, "US")
    L4.config(state=DISABLED)
    
    #return IPA

#THIS FUNCTION PRIMARILY HANDLES KL DOWNLOAD AND PARSING AND UPDATES INFORMATION IN THE BOTTOM TEXT BOX
def getkl(ip):
    global VLT #VOLTAGE "1380"
    global MOD #MODEL NUMBER SHORTHAND "S19+"
    MOD = ""
    VLT = ""
    ftps=["","",""] #USED FOR PARSING OUT MODEL FROM API
    t = "" #USED FOR RETURN MODEL TYPE (FOR TL DISPLAY)
    ra = "" #USED FOR RECC ACTIONS (TR DISPLAY)
    flags = [0,0,0,0,0,0] #to limit over-parsing
    h = "" #this is in my return and im too lazy now
    #regi = [0,0,0,0] supeceded by RAT and CHN method
    data = CgminerAPI(ip).stats()
    try:
        try:
            ftps = data['STATS'][0]['Type'].split()[1:]
            MOD = ftps[0]
            #print(str(x) +" "+MOD)
            if (MOD == "L5"):
                BOA = 4
            else:
                BOA = 3
            for i in range(BOA):
                ASC[i]=str(data['STATS'][1][f'chain_acn{(i+1)}'])


        except KeyError:
            print( "getkl: Error getting stats, is miner online?")
            #MOD = "X17"
            BOA = 3
            ra += "CONNECTION LOST, SOC_INIT? CHECK CONTROL BOARD\n"
        except IndexError:
            print( "getkl: Error getting stats, JSON index invalid.")
            #MOD = "X17"
            BOA = 3
            ra += "CONNECTION LOST, SOC_INIT? CHECK CONTROL BOARD\n"

        print("Downloading Kernel Log, Please Wait...")
        sMOD= MOD.strip('+')
        #S19 has a different log url so...
        if (sMOD[0:3] == 'S19'):
            url = f'http://{ip}/cgi-bin/log.cgi'
            response = requests.get(url, auth=HTTPDigestAuth(USR, PSS), timeout=1)

        else:
            url = f'http://{ip}/cgi-bin/get_kernel_log.cgi'
            response = requests.get(url, auth=HTTPDigestAuth(USR, PSS), timeout=1)
        y = response.text

        t = f"{ip} Miner Type:" 
        for inf in ftps[0:]: #i love this trick remember that, [0:] is the whole list
            t = t + " " + inf
        
        #BEGIN LOG PARSING
        lines = y.split('\n')
        count = 0
        perc = 0
        exp = int(len(lines)/10)
        print (f"Begin Parsing {len(lines)} lines, wait")
        for line in (lines):
            count+=1

            
            if (count%exp==0):
                perc += 10
                print(f"\t{perc}% -- Line {count} of {len(lines)}")

                
            if ('Chain[' in line):
                al = line.split("[")
                c = int(al[1][0:1])
                ASC[c]=al[1].split(" ")[2]
                
                
            elif ('over max temp,' in line):
                if (sMOD[0:3] == 'S19'):
                    if (int(line.split()[7]) == 0):
                        ra = ra + "Bad Temp Sensor Found -> PT1 all boards\n"
                    elif (int(line.split()[7]) == 255):
                        ra = f"{ra}Bad Data Connection -> Check HB Data Cables\n"
                    else:
                        ra = f"{ra}Overheating Detected -> See Values -> Send Boards to Repair\n"
                        ra = f"{ra}PCB: {line.split()[7]} (MAX {line.split()[9][0:2]})\n"
                        ra = f"{ra}CHIP: {line.split()[12][0:2]} (MAX {line.split()[13][0:2]})\n\n"
                else:
                    ra = f"{ra}Overheating Detected, Evaluate KL"

            elif ('voltage[' in line) or ((sMOD[0:3] == 'S19') and ('working voltage =' in line)):
                vs = line.split("=")
                VLT = vs[1][1:5]
                #print("voltage" + str(vs))
                
            elif ((ftps[0] == 'K5') and ('get vol' in line)):
                vs = line.split()
                VLT = vs[19]

            elif (('EEPROM' in line) or ('stop_mining' in line)) and flags[2]<1:
                flags[2]+=1
                ra = ra + f"EVALUATE FIRMWARE, NETWORK, POOL INFO, AND FANS\n"


            elif ('power voltage can not' in line or 'chain avg vol drop' in line) and flags[4]<1:
                flags[4]+=1
                ra = ra + f"Check 4-Pin PSU Cable and Output Voltage on Terminals; Swap PSU\n"


    except requests.ConnectTimeout as e:
        print (f"Connection Timeout, is the VPN Connection Live? {e}")
        y = f"Connection Timeout, is the VPN Connection Live?\n{e}"
        t = "Unknown Antminer"

    except requests.ConnectionError as e:
        print (f"Connection Error, is the Miner WEB GUI accessible? {e}")
        y = f"Connection Error, miner returned no data.\n{e}"
        t = "Unknown Antminer"
        ra = f"{ra}Flash Recovery (else) Replace Control Board"
    
    except IndexError as e:
        print (f"Index Error, Error in get_system_info {e}")
        y = "Index Error, Error in get_system_info"
        t = "Unknown Antminer"
    print( f"Parsing Finished, displaying {ip}\n")
    ret = [y, h, t, ra]
    return ret


#THIS FUNCTION PRIMARILY MAKES API CALLS AND FEEDS INFORMATION INTO THE TOP LEFT BOX
def prints(ip):
    global TMP
    global IDL
    global RAT
    global DED
    data = CgminerAPI(ip).stats()
    b = "" #Text for print window
    ba = ""
    
    TMP = [[],[],[]] 
    RAT = [0,0,0]
    IDL = 0
    DED = 0

    #Evaluate all fans, FW errors are caught here
    for i in range(len(FAN)):
        try:
            FAN[i]=data['STATS'][1][f'fan{i+1}']
        except KeyError as e:
            FAN[i] = "KE"
        except IndexError as e:
            FAN[i] = "KE"

    #Im gonna try to determine the level of the boards for only S19+
    """
    01-01 05:20:22 level 1, voltage = 1350 frequency = 695
    01-01 05:20:22 level 2, voltage = 1360 frequency = 695
    01-01 05:20:22 level 3, voltage = 1380 frequency = 695
    01-01 05:20:22 level 4, voltage = 1360 frequency = 670
    01-01 05:20:22 level 5, voltage = 1380 frequency = 670
    01-01 05:20:22 level 6, voltage = 1400 frequency = 670
    01-01 05:20:22 level 7, voltage = 1380 frequency = 645
    01-01 05:20:22 level 8, voltage = 1400 frequency = 645
    01-01 05:20:22 level 9, voltage = 1420 frequency = 645
    """
    lvl = [1,1,1]
    if (MOD == "S19+"):
        ldict = {
        1: [1350, 695],
        2: [1360, 695],
        3: [1380, 695],
        4: [1360, 670],
        5: [1380, 670],
        6: [1400, 670],
        7: [1380, 645],
        8: [1400, 645],
        9: [1420, 645],
        }
        klist = list(ldict.keys())
        vlist = list(ldict.values())
        for c in range(3):
            frq = data['STATS'][1][f'freq{c+1}']
            if (VLT != "" and frq != 0):
                try:
                    pos = klist[vlist.index([int(VLT), frq])]
                    lvl[c] = pos
                except Exception as e:
                    lvl[c] = 0

    
    #determine the ideal rate of the miner
    try:
        IDL = data['STATS'][1]['total_rateideal']
        b = "Current Hashrate: " + str(data['STATS'][1]['GHS 5s']) + "Gh\s"
        b = f"{b}\nFan Speeds: {str(FAN)}\n\n"
        
        #evaluate each board for hashrate
        #NC or 0hr will come back as a failure so we catch it
        #encoding errors as "x" allows me to filter them out easily
        for c in range(BOA):
            try:
                i = float(data['STATS'][1][f'chain_rate{c+1}'])
            except Exception as e:
                i = 'x'
            RAT[c] = i
            #Total printout of all chains and working status
            #Kindof a beefy block but it does a lot
            b += f"Chain {(c+1)}: {ASC[c]} ASIC\n"
            if data['STATS'][1][f'chain_acs{(c+1)}'] != "":
                b += f"Chain {(c+1)}: {data['STATS'][1][f'chain_rate{(c+1)}']} Gh\s -- TEMP: {data['STATS'][1][f'temp_pcb{(c+1)}']}\n"
                TMP[c]=data['STATS'][1][f'temp_pcb{(c+1)}'].split("-")
                b += str(data['STATS'][1]['chain_acs'+str(c+1)]) + "\n"
                if (MOD == "K5"):
                    b += f"Chain {(c+1)} {VLT} V / {data['STATS'][1]['frequency']} Hz\n\n"
                else:
                    b += f"Chain {(c+1)}: L{lvl[c]} -- {VLT} V / {data['STATS'][1][f'freq{(c+1)}']} Hz \n\n"
            else:
                b += f"CHAIN {(c+1)} FAILURE STATE, COUNT {ASC[c]} ASIC!!\n\n"
                ba += f"Chain {(c+1)}*"
                DED += 1
    
    except KeyError as e:
        b = f"prints: Error getting stats, is miner online? {e}\n{str(data)}"
    
    except IndexError as e:
        b = f"prints: Error getting stats, JSON index invalid. {e}\n{str(data)}"
    
    return (b,ba)


def reccomend(klr, bcc):
    r = f"RECCOMENDED ACTIONS:\n{klr}"
    #Get an average of the running fans
    bun = FAN[:]
    base = 0
    work = 0
    for x in range(len(FAN)):
        if (bun[x] == "KE" or bun[x] == 0 or bun[x] > 10000):
            bun[x] = 0
        else:
            work = work + 1
        base = base + int(bun[x])
    if (not work == 0):    
        base = base/work
    else:
        base = 0

    #Sometimes fans' info is not recieved by FW, indicative of another issue
    for i in range(len(FAN)):
        if (FAN[i] == "KE"):
            r += f"Evaluate Firmware, Fan {i+1} not found by API.\n"
            #or FAN[i] > base+(base*0.3)    
        elif (FAN[i] == 0 or FAN[i] > 10000 or FAN[i] < base-(base*0.2)):
            r += f"Replace Fan {i+1}.\n"

    #Evaluate the hashrate of each board against the ideal/working
    for idx, rate in enumerate(RAT):
        if (rate != 'x' and DED<BOA):
            if (MOD.strip("+")=="S19" and (float(rate) < (float(IDL/(BOA-DED)) - (float((IDL/(BOA-DED))*.12))))):
                r += f"CHAIN {idx+1} LOW HASHRATE -> TO REPAIRS PT2\n"          
            elif(MOD.strip("+")[1:]=="17" and (float(rate) < (float(IDL/(BOA-DED)) - (float((IDL/(BOA-DED))*.12))))):
                r += f"CHAIN {idx+1} LOW HASHRATE -> TO REPAIRS PT2\n"

    #Temp sensor troubles, this is to catch "flat" sensors
    for idx, t in enumerate(TMP):
        for s in range(len(t)):
            try:
                if (int(t[s]) <= 10):
                    r = f"{r}Chain {idx+1} Sensor {s} NG -> To Repairs\n"
            except ValueError as e:
                r = f"{r}Fail to read TS{s} on CH{idx+1}\n"

    if (len(bcc)-1 > 0):
        #r = f"{r}\nONLY IF ALL OTHER COMPONENTS ARE VERIFIED FUNCTIONAL:\n"
        for i in range(len(bcc)-1):
            r = f"{r}Remove {bcc[i]} For PT1 Test\n"

             
    r = f"{r}\nIf you see duplicates/old data here, update firmware.\n"

    return r

def gui():
    url = 'https://'+USR+":"+PSS+'@'+IPA
    webbrowser.open(url)
def nonce():
    #Child Window
    child = Toplevel(top)
    child.state('withdrawn')
    child.title("Sub Window")
    dX = 760
    dY = 360
    default = str(dX) + "x" + str(dY)
    child.geometry(default)
    
    
    noframe = Frame(child, height="360" )
    NL1 = Label(noframe, text = "Nonce")
    NL1.pack( side = TOP)
    NT1 = tks.ScrolledText(noframe, width=42)
    NT1.pack(fill=Y,  expand=1)
    NT1.tag_add("bla", '1.8', '1.13')
    NT1.tag_add("red", '1.8', '1.13')
    NT1.tag_config("bla", foreground = "black")
    NT1.tag_config("red", foreground = "red")
    noframe.pack(fill=X, expand=1, side = LEFT)
    
    adframe = Frame(child)# , width=int(dW)+20)#, width="50")
    NL3 = Label(adframe, text = "ADC")
    NL3.pack( side = TOP)
    NT3 = tks.ScrolledText(adframe)#, width=int(dW))
    NT3.pack(fill=Y)#expand=1)
    NT3.tag_add("bla", '1.8', '1.13')
    NT3.tag_add("red", '1.8', '1.13')
    NT3.tag_config("bla", foreground = "black")
    NT3.tag_config("red", foreground = "red")
    adframe.pack(fill=X, side=RIGHT)#expand=1, side=RIGHT)
    
    NT1.config(state=NORMAL)
    NT1.delete('1.0', END)
    NT3.config(state=NORMAL)
    NT3.delete('1.0', END)
    
    try:
        nurl = f'http://{IPA}:6060/nonce'
        n = requests.get(nurl, auth=HTTPDigestAuth(USR, PSS), timeout=1)
        y = n.text
            
        arr=[[],[],[]]
        chn = int()
        asc = int()
        s = y.split("\n")
         
        #s = noncedummy.split('\n')
        for line in s:
            #s = line.split()
            if (line!=""):
                x = line.split()
                
                
                for verb in x:
                    
                    if (verb[:4] == "chai"):
                        #print("Chain: " + verb.split("[")[1][:1])
                        chn = int(verb.split("[")[1][:1])
                        
                    if ((verb[:4] == "asic") and (len(verb)>4)):
                        #print(verb)
                        #print(verb.split("=")[1])
                        asc = int(verb.split("=")[0].split("[")[1][:3])
                        rate = int(verb.split("=")[1])
                        arr[chn].insert(len(arr[chn]),[asc,rate,""])
        
        #arr at this point should be a full array of asics    
        count = 0            
        for board in arr:
            
            #print (f"Chain {count}:")
            NT1.insert(END, f"Chain {count}:\n")
            
            boardsum=0

            boardavg=0
            
            for asic in board:
                boardsum+=asic[1]
            
            if (len(board)>0):
                boardavg=boardsum/len(board)
                threshold = (boardavg-(boardavg*.10))
                othreshold = (boardavg+(boardavg*.30))
                
                for asic in board:
                    #print (str(asic))
                    if ((asic[1] < threshold)):
                        asic[2] = "FAIL"
                        NT1.insert(END, str(asic)+" min:"+str(int(threshold))+" max:"+str(int(othreshold))+"\n","red")
                    else:
                        asic[2] = "OK"
                        NT1.insert(END, str(asic)+" min:"+str(int(threshold))+" max:"+str(int(othreshold))+"\n","bla")
                    
                        
                    
            
            count+=1
                
    except requests.ConnectTimeout as e:
        #print (f"Connection Timeout, is the VPN Connection Live? {e}")
        NT1.insert(END, f"Could not connect to {IPA}")
    except NameError as n:
        NT1.insert(END, f"No IP configured")            
            
            
            #NT1.insert(END, str(line) +"\n")
    
    
    arr=[[],[],[]]
    chn = int()
    asc = int()
            
    try:
        nurl = f'http://{IPA}:6060/adc'
        n = requests.get(nurl, auth=HTTPDigestAuth(USR, PSS), timeout=1)
        y = n.text
        #y=adcdummy
        s = y.split('\n')
        for line in s:
            x = line.split()
                
            countv = 0
            
            for verb in x:
                #NT3.insert(END, str(verb))
                
                if (verb[:4] == "chai"):
                    chn = int(x[countv+1])
            
                if ((verb == "asic")):
                    asc = int(x[countv+1])
                    d0 = (x[countv+3])
                    d1 = (x[countv+4])
                    d2 = (x[countv+5])
                    d3 = (x[countv+6])
                    asu = (x[countv+7])
                    avg = (x[countv+8])
                    
                    arr[chn].insert(len(arr[chn]),[asc,d0,d1,d2,d3,asu,avg])
                countv+=1
                #arr at this point should be a full array of asics    
        count = 0            
        for board in arr:
            
            for asic in board:
                if (((1.45 > float(asic[5]) > 1.25)) and ((0.40 > float(asic[6]) > 0.30))):
                    NT3.insert(END, (f"{asic[0]}:{asic[1]}\\"+
                    f"{asic[2]}\\{asic[3]}\\{asic[4]}"+
                    f" -- S: {asic[5]} A: {asic[6]}\n"), "bla")
                else:
                    NT3.insert(END, (f"{asic[0]}:{asic[1]}\\"+
                    f"{asic[2]}\\{asic[3]}\\{asic[4]}"+
                    f" -- S: {asic[5]} A: {asic[6]}\n"), "red")
            
            count+=1
            
    except requests.ConnectTimeout as e:
        NT3.insert(END, f"Could not connect to {IPA}")

    except NameError as n:
        NT3.insert(END, f"No IP configured")
   
    
    NT1.config(state=DISABLED)
    NT3.config(state=DISABLED)
    child.state('normal')
    child.lift()
    
def makef():
    ## Make the file
    
    x=""
    if len(IPS) < 4 or len(IPS) > 4:
        x = "error"

    if(x!="error"):
        L4.config(state=NORMAL)
        L4.delete('1.0', END)
        today = datetime.now()
        filename = "logs/" + today.strftime("%#m-%d-%Y %H-%M-%S") + ' -- '  + f'{IPS[0]}x{IPS[1]}x{IPS[2]}x{IPS[3]}' + '.txt'
        f = open(filename, 'a+')
        f.write(TYP + "\n")
        f.write("Log Date: " + today.strftime("%#m-%d-%Y %H-%M-%S") + "\n")
        f.write(STS + "\n")
        f.write(RKL + "\n")
        f.close
        L4.insert(END, "S")
        L4.config(state=DISABLED)
    else:
        print("error prevented saving")


#EVENT HANDLING        
def enterKey(event):
    pullInfo(ip_var.get())


def bhelp():
    global BNK
    if (BNK == "off"):
        if (MOD == "S19"):
            #This works for S19!
            payload ={"blink": "true"}
            url = f'http://{IPA}/cgi-bin/blink.cgi'
            response = requests.post(url, auth=HTTPDigestAuth(USR, PSS), json = payload)

        else:
            #X17....
            payload = "action=startBlink"
            url = f'http://{IPA}/cgi-bin/blink.cgi'

            try:
                response = requests.post(url, auth=HTTPDigestAuth(USR, PSS), data = payload, timeout=1)
            except requests.exceptions.ReadTimeout:
                response = "I'm an X17 response, I'm blinking!"
        #print (response)
        BNK = "on"

    elif (BNK == "on"):
        if (MOD == "S19"):
            #This works for S19!
            payload ={
                "blink": "false"}
            url = f'http://{IPA}/cgi-bin/blink.cgi'
            response = requests.post(url, auth=HTTPDigestAuth(USR, PSS), json = payload)
        else:
            #X17....
            payload = "action=stopBlink"
            url = f'http://{IPA}/cgi-bin/blink.cgi'
            try:
                response = requests.post(url, auth=HTTPDigestAuth(USR, PSS), data = payload, timeout=1)
            except requests.exceptions.ReadTimeout:
                #print ("Sent blink command to X17, safely crashing the request")
                response = "I'm an X17 response, I'm no longer blinking!"
        #print (response)
        BNK = "off"

    else:
        BNK = "off"
        
    
if __name__ == '__main__':
    #Build window

    top = Tk()
    
    top.title("KG's Kick-Ass Kernel Log Puller")
    dX = 720
    dY = 420
    default = str(dX) + "x" + str(dY)
    top.geometry(default)
    top.state('normal')
    
    frame = Frame(top)
    frame.pack(expand=1)

    #Bind Enter to a keypress
    top.bind('<Return>', enterKey)

    #Assign Variable for storing IP ADDR
    ip_var=StringVar()
    usr_var=StringVar()
    pss_var=StringVar()
    saved_var=StringVar()
    AS = IntVar()
    
    AS.set(0)
    saved_var = ""
    

    L2 = Label(frame, text = "U")
    L2.pack( side = LEFT)
    #User Entry
    E2 = Entry(frame, textvariable = usr_var, bd = 5, width = 4)
    E2.insert(0,"root")
    E2.pack(side = LEFT)

    L3 = Label(frame, text = "P")
    L3.pack( side = LEFT)
    #Pass Entry
    E3 = Entry(frame, textvariable = pss_var, bd = 5, width = 2)
    E3.pack(side = LEFT)

    L7 = Label(frame, text = "IP", width=2)
    L7.pack( side = LEFT)
    #IP Entry
    E1 = Entry(frame, textvariable = ip_var, bd = 5, width = 10)
    E1.pack(side = LEFT)

    E2.focus_set()

    #Save Button
    B1 = Button(frame, text = "SAVE", command = makef)
    B1.pack(side=LEFT)
    
    
    B2 = Button(frame, text = "BLINK", command = bhelp)#blink)
    B2.pack(side=LEFT)
    
    B3 = Button(frame, text = "NONCE", command = nonce)#blink)
    B3.pack(side=LEFT)
    
    B4 = Button(frame, text = "GUI", command = gui)#blink)
    B4.pack(side=LEFT)

    L4 = Text(frame, height=1, width=4)
    L4.insert(END,saved_var)
    L4.config(state=DISABLED)
    
    L4.pack(side = LEFT, after=B1)

    
    A1 = Checkbutton(frame, text="Autosave", variable=AS)
    A1.pack(side = LEFT, after=L4)

    frame2 = Frame(top)
    frame2.pack(expand=1)

    frame3 = Frame(frame2)
    frame3.pack(expand=1)
    
    
    #Top Panel, Stats and Errors
    exframe = Frame (top, height="100")
    
    dW = int(((exframe.winfo_screenwidth()/2)/10))
    
    #Stats
    stframe = Frame(exframe)#, width=int(dW))#, width="50")
    
    L2 = Label(stframe, text = "ST")
    L2.pack( side = TOP)
    T2 = tks.ScrolledText(stframe, height="11", width="50")
    T2.pack()#expand=1)
    stframe.pack(fill=X, side=LEFT)#expand=1, side=LEFT)

    #Errors
    erframe = Frame(exframe)# , width=int(dW)+20)#, width="50")
    L3 = Label(erframe, text = "ET")
    L3.pack( side = TOP)
    T3 = tks.ScrolledText(erframe, height="11")#, width=int(dW))
    T3.pack()#expand=1)
    
    erframe.pack(fill=X, side=RIGHT)#expand=1, side=RIGHT)

    exframe.pack(fill=X, expand=1, side = TOP)
    
    #Kernel Log Window
    klframe = Frame(top, height="200" )
    L1 = Label(klframe, text = "KL")
    L1.pack( side = TOP)
    T1 = tks.ScrolledText(klframe)
    T1.pack(fill=BOTH, expand=1)
    klframe.pack(fill=X, expand=1, side = BOTTOM)

    
    
    top.mainloop()
