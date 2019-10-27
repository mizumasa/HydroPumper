
""" sending OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation
"""
import OSC
import time, random
import os, sys
import threading

TAB_IPS =[
    "192.168.11.1",
    "192.168.11.2",
    "192.168.11.3"
]
TAB_PORT = 12346
GUN_IPS =[
    "192.168.11.5",
    "192.168.11.6",
    "192.168.11.7"
]
GUN_PORT = 12346
PC_IP = "192.168.11.20"
PC_PORT = 12345

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
        self.localMode = False
        self.debug = False
        return
    def setLocal(self):
        self.myIP = LOCAL_IP
        self.localMode = True
    def setDebug(self):
        self.debug = True

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
                print "send to ",i
                self.client.sendto(msg, (i, port))
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
            self.client.sendto(msg,(LOCAL_IP, TAB_PORT))
        else:
            self.sendAll(msg, [TAB_IPS[idx]], TAB_PORT)
        return

    def sendTabAll(self, address, content):
        msg = self.makeMsg(address,content)
        try:
            if self.localMode:
                print("send to "+LOCAL_IP)
                self.client.sendto(msg,(LOCAL_IP, TAB_PORT))
            else:
                self.sendAll(msg, TAB_IPS, TAB_PORT)
        except:
            print("sendTabAll error")
        return

    def sendGun(self, address, content, idx):
        msg = self.makeMsg(address,content)
        if self.localMode:
            self.client.sendto(msg,(LOCAL_IP, GUN_PORT))
        else:
            self.sendAll(msg, [GUN_IPS[idx]], GUN_PORT)
        return

    def sendGunAll(self, address, content):
        msg = self.makeMsg(address,content)
        if self.localMode:
            self.client.sendto(msg,(LOCAL_IP, GUN_PORT))
        else:
            self.sendAll(msg, GUN_IPS, GUN_PORT)
        return


def main():
    pass


if __name__=='__main__':
    argvs=sys.argv
    print argvs
    main()