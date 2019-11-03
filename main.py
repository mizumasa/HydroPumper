
""" sending OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation
"""
import libOSC
import libWindow
import time, random
import os, sys
from copy import deepcopy

STAGE_INIT = 0
STAGE_COUNTDOWN = 1
STAGE_LEVEL_1 = 2
STAGE_LEVEL_2 = 3
STAGE_LEVEL_3 = 4
STAGE_END = 5
STAGE_RESULT = 6

FPS = 30

MATO1_STATUS_OFFSET = 100
MATO2_STATUS_OFFSET = 400

def setAllTab(tab,state):
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            tab[i][j] = state

def setAllGun(gun,state):
    for i in range(len(gun)):
        for j in range(len(gun[i])):
            gun[i][j] = state

def initState(tab,gun):
    setAllTab(tab,1)
    setAllGun(gun,1)

def startState(tab,gun):
    setAllTab(tab,10)
    setAllGun(gun,10)

def countdownState(tab,gun):
    setAllTab(tab,2)
    setAllGun(gun,2)

def tabStateToColor(state):
    if state == 1:# logo
        return [255,255,0]
    if state == 2:# count down
        return [255,255,255]
    if state == 10:# no mato
        return [0,0,0]
    if state >= MATO1_STATUS_OFFSET and state <= MATO1_STATUS_OFFSET+200:# mato
        return [state + 50 - MATO1_STATUS_OFFSET, 100, 100]
    if state >= MATO2_STATUS_OFFSET and state <= MATO2_STATUS_OFFSET+200:# item mato
        return [100, state + 50 - MATO2_STATUS_OFFSET, 100]
    return [0,0,0]

def updateStateTab(state):
    if state == MATO1_STATUS_OFFSET:
        return 10
    if state > MATO1_STATUS_OFFSET and state <= MATO1_STATUS_OFFSET+200:# no mato
        return state - 1
    if state == MATO2_STATUS_OFFSET:
        return 10
    if state > MATO2_STATUS_OFFSET and state <= MATO2_STATUS_OFFSET+200:# item mato
        return state - 1
    return state

def updateStateGun(state):
    return state

def updateState(tab,gun):
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            tab[i][j] = updateStateTab(tab[i][j])
    for i in range(len(gun)):
        for j in range(len(gun[i])):
            gun[i][j] = updateStateGun(gun[i][j])

def printState(tab,gun):
    for i in range(len(tab)):
        print("tab"+str(i),tab[i])
    for i in range(len(gun)):
        print("gun"+str(i),gun[i])
    return

def debugState(tab,gun,window):
    for i in range(len(tab)):
        window.setData("tab"+str(i),tab[i])
    for i in range(len(gun)):
        window.setData("gun"+str(i),gun[i])
    return

def main(argvs):
    mode = None
    osc = libOSC.MY_OSC()
    for i in argvs:
        if "debug" == i:
            osc.setDebug()
    GUN_MODE = [[0]]
    TAB_MODE = [[0,1,2,3,4,5,6,7,8,9]]
    if len(argvs) > 1:
        mode = argvs[1]
        if mode == "local":
            osc.setLocal()
            GUN_MODE = [[0]]
            TAB_MODE = [[0]]
        if mode == "1":#single mode
            GUN_MODE = [[0]]
            TAB_MODE = [[0,1,2,3,4,5,6,7,8,9]]
        if mode == "2":#battle mode
            GUN_MODE = [[0],[1]]
            TAB_MODE = [[0,1,2,3,4],[5,6,7,8,9]]
        if mode == "3":#collab mode
            GUN_MODE = [[0,1]]
            TAB_MODE = [[0,1,2,3,4,5,6,7,8,9]]
    userDict = makeDictIp2User(libOSC.TAB_IPS, TAB_MODE)
    tabState = deepcopy(TAB_MODE)
    gunState = deepcopy(GUN_MODE)
    initState(tabState,gunState)
    osc.setup()
    count = 0
    stage = STAGE_INIT
    stagePre = STAGE_INIT
    timeScale = 1.0
    window = libWindow.DEBUG_WINDOW()
    debugState(tabState,gunState,window)

    while 1:
        if count > 0:
            count += 1
            # change stage
            # update each frame
            stage = update(count,stage,timeScale,tabState,gunState,osc,window)
            time.sleep(1/30.)
            if count % FPS == 0:
                print("["+str(count/FPS)+"]"+str(stage))
                score = calcScore(len(TAB_MODE), userDict, osc.recv)
        # action when stage changed
        if stagePre != stage:
            print("change stage to" + str(stage))
            if stage == STAGE_COUNTDOWN:
                countdownState(tabState,gunState)
                osc.sendTabAll("/start",[])
            if stage == STAGE_LEVEL_1:
                startState(tabState,gunState)
            if stage == STAGE_LEVEL_3:
                osc.sendTabAll("/level",[3])
            if stage == STAGE_INIT:
                count = 0
        debugState(tabState,gunState,window)
        stagePre = stage

        key = window.update()
        if key == ord('q'):
            window.close()
            osc.kill()
            break
        if key == ord('s'):
            stage = STAGE_COUNTDOWN
            count = 1
        if key == ord('i'):
            stage = STAGE_INIT
            count = 0

    pass


def makeDictIp2User(TAB_IPS, TAB_MODE):
    out = {}
    for i in range(len(TAB_MODE)):
        for j in TAB_MODE[i]:
            out[TAB_IPS[j]] = i
    return out

def calcScore(userNum, userDict, oscRecvList):
    print("User num = "+str(userNum))
    score = [0,] * userNum
    for i in oscRecvList:
        if i[1] == '/hit':
            if i[0][0] in userDict.keys():
                score[ userDict[i[0][0]] ] += i[2]
            else:
                score[0] += i[2]
    print("score:",score)
    return score

def update(count,stage,timeScale,tabState,gunState,osc,window):
    #print("count", count,"stage",stage)
    if count == int(4 * FPS * timeScale):
        stage = STAGE_LEVEL_1
        osc.clearRecv()
        print("change to STAGE_LEVEL_1")
    if count == int(7 * FPS  * timeScale):
        print("change to STAGE_LEVEL_2")
        stage = STAGE_LEVEL_2
    if count == int(9 * FPS  * timeScale):
        stage = STAGE_LEVEL_3
    if count == int(12 * FPS  * timeScale):
        osc.sendTabAll("/end",[])
        stage = STAGE_END
    if count == int(15 * FPS  * timeScale):
        osc.sendTabAll("/result",[777])
        stage = STAGE_RESULT
    if count == int(17 * FPS  * timeScale):
        osc.sendTabAll("/init",[])
        stage = STAGE_INIT
        osc.clearRecv()

    if stage == STAGE_LEVEL_1:
        for tabList in tabState:
            if random.random() > 0.5:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    tabList[idx] = MATO1_STATUS_OFFSET + 30
                    osc.sendTabAll("/up",[2000])
    if stage == STAGE_LEVEL_2:
        for tabList in tabState:
            if random.random() > 0.5:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    tabList[idx] = MATO1_STATUS_OFFSET + 30
                    osc.sendTabAll("/up",[1500])
    if stage == STAGE_LEVEL_3:
        for tabList in tabState:
            if random.random() > 0.5:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    tabList[idx] = MATO1_STATUS_OFFSET + 30
                    osc.sendTabAll("/up",[1000])
    updateState(tabState,gunState)
    #printState(tabState,gunState)
    return stage
    
if __name__=='__main__':
    argvs=sys.argv
    print(argvs)
    main(argvs)