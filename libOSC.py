
""" sending OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation
"""
import OSC
import time, random
import os, sys
import threading

IP_HEAD = "192.168.1."

TAB_IPS =[
    IP_HEAD+"1",
    IP_HEAD+"2",
    IP_HEAD+"3"
]
TAB_IPS =[
    IP_HEAD+"11",
    IP_HEAD+"12",
    IP_HEAD+"13",
    IP_HEAD+"14",
    IP_HEAD+"15",
    IP_HEAD+"16",
    IP_HEAD+"17",
    IP_HEAD+"18",
    IP_HEAD+"19",
    IP_HEAD+"20",
    IP_HEAD+"21",
    IP_HEAD+"22"
]

TAB_IPS =[
    IP_HEAD+"14",
    IP_HEAD+"12",
    IP_HEAD+"22",
    IP_HEAD+"18",
    IP_HEAD+"15",
    IP_HEAD+"17"
    ]

TAB_IPS2 =[
    IP_HEAD+"101"
]

TAB_PORT = 12346
GUN_IPS =[
    IP_HEAD+"5",
    IP_HEAD+"6",
    IP_HEAD+"7"
]
GUN_IPS =[
    IP_HEAD+"11",
    IP_HEAD+"12",
    IP_HEAD+"13",
    IP_HEAD+"14",
    IP_HEAD+"15",
    IP_HEAD+"16",
    IP_HEAD+"17",
    IP_HEAD+"18",
    IP_HEAD+"19",
    IP_HEAD+"20"
]
GUN_IPS =[
    IP_HEAD+"40",
    IP_HEAD+"41",
    IP_HEAD+"42",
    IP_HEAD+"43",
    IP_HEAD+"44"
]

GUN_PORT = 12346
PC_IP = IP_HEAD+"50"
PC_PORT = 12345
PC_LOCAL_PORT = 12349
PC_LOCAL_IP = PC_IP

LOCAL_IP = '127.0.0.1'

class MY_OSC:
    def __init__(self):
        self.myIP = PC_IP
        self.myPORT = PC_PORT
        self.ip = ""
        self.host = ""
        self.dst = []
        self.bArrived = False
        self.recv = []
        self.recvItem = []
        self.localMode = False
        self.debug = False
        return
    def setLocal(self):
        self.myIP = LOCAL_IP
        self.localMode = True
    def setDebug(self):
        self.debug = True

    def client_sendto(self,msg,path):
        try:
            self.client.sendto(msg,path)
        except:
            print("send error",msg,path)

    def sendStartAudio(self):
        msg = self.makeMsg("/startaudio",[])
        if self.debug:
            print("Send start audio to ", PC_LOCAL_PORT, msg)
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))

    def sendAudioMode(self,iMode):
        msg = self.makeMsg("/audio",[iMode])
        if self.debug:
            print("Send audio mode to ", PC_LOCAL_PORT, msg)
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))

    def sendAudioLevel(self,level):
        msg = self.makeMsg("/audiolevel",[level])
        if self.debug:
            print("Send audio level to ", PC_LOCAL_PORT, msg)
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))
        self.client_sendto(msg,(PC_LOCAL_IP, PC_LOCAL_PORT))

    def myMsgPrinter_handler(self, addr, tags, data, client_address):
        print "osc://%server%server ->" % (OSC.getUrlStr(client_address), addr),
        print "(tags, data): (%server, %server)" % (tags, data)

    def myMsg_handler(self, addr, tags, data, client_address):
        print "(tags, data): (%s, %s)" % (tags, data)
        self.bArrived = True
        self.recv.append([client_address,addr,data[0]])

    def hit_handler(self, addr, tags, data, client_address):
        print "(tags, data): (%s, %s)" % (tags, data)
        print "hit !!!!!!!!!!!!!!!!!!!"
        self.bArrived = True
        self.recv.append([client_address,addr,data[0]])

    def hititem_handler(self, addr, tags, data, client_address):
        print "(tags, data): (%s, %s)" % (tags, data)
        print "hit item!!!!!!!!!!!!!!!!!!!"
        self.bArrived = True
        self.recv.append([client_address,addr,data[0]])
        self.recvItem.append([client_address,0])

    def setup(self):
        print("work as server",self.myIP,self.myPORT)
        self.server = OSC.OSCServer((self.myIP,self.myPORT))
        self.server.addDefaultHandlers()
        self.server.addMsgHandler("/print", self.myMsgPrinter_handler)
        self.server.addMsgHandler("/msg", self.myMsg_handler)
        self.server.addMsgHandler("/hit", self.hit_handler)
        self.server.addMsgHandler("/hititem", self.hititem_handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        self.client = OSC.OSCClient()
        return

    def clearRecv(self):
        self.recv = []
        self.recvItem = []

    def get(self):
        if self.bArrived:
            ret = self.recv
            self.recv = []
            self.bArrived = False
            return ret
        return None
    def kill(self):
        try:
            self.server.close()
            print "server closed 1"
            self.server_thread.join()
        except:
            print "first error"
            try:
                self.server.close()
                print "server closed 2"
                self.server_thread.join()
            except:
                print "seccond error"
                pass
            pass

    def sendAll(self, msg, ips, port):
        for i in ips:
            try:
                if self.debug:
                    print("Send to ",i,port,msg)
                self.client_sendto(msg, (i, port))
            except:
                print "send error"

    def makeMsg(self, address, content):
        msg = OSC.OSCMessage(address)
        for i in content:
            msg.append(i)
        return msg

    def sendTab(self, address, content, idx):
        msg = self.makeMsg(address,content)
        if self.localMode:
            if self.debug:
                print("Send tab to ", LOCAL_IP, TAB_PORT, msg)
            self.client_sendto(msg,(LOCAL_IP, TAB_PORT))
        else:
            self.sendAll(msg, [TAB_IPS[idx]], TAB_PORT)
        return

    def sendTabAll(self, address, content):
        msg = self.makeMsg(address,content)
        try:
            if self.localMode:
                if self.debug:
                    print("Send tab to ",LOCAL_IP, TAB_PORT, msg)
                self.client_sendto(msg,(LOCAL_IP, TAB_PORT))
            else:
                self.sendAll(msg, TAB_IPS, TAB_PORT)
        except:
            print("sendTabAll error")
        return

    def sendGun(self, address, content, idx):
        msg = self.makeMsg(address,content)
        if self.localMode:
            if self.debug:
                print("Send gun to ",LOCAL_IP,msg)
            self.client_sendto(msg,(LOCAL_IP, GUN_PORT))
        else:
            self.sendAll(msg, [GUN_IPS[idx]], GUN_PORT)
        return

    def sendGunAll(self, address, content):
        msg = self.makeMsg(address,content)
        if self.localMode:
            if self.debug:
                print("Send gun to ",LOCAL_IP,msg)
            self.client_sendto(msg,(LOCAL_IP, GUN_PORT))
        else:
            self.sendAll(msg, GUN_IPS, GUN_PORT)
        return


def main():
    pass


if __name__=='__main__':
    argvs=sys.argv
    print argvs
    main()