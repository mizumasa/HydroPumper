
""" sending OSC with pyOSC
https://trac.v2.nl/wiki/pyOSC
example by www.ixi-audio.net based on pyOSC documentation
"""


import libOSC
import libWindow
import time, random
import os, sys
from copy import deepcopy

LEVEL_RATIO = 500.

STAGE_INIT = 0
STAGE_COUNTDOWN = 1
STAGE_LEVEL_1 = 2
STAGE_LEVEL_2 = 3
STAGE_LEVEL_3 = 4
STAGE_END = 5
STAGE_RESULT = 6
STAGE_RANK = 7

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
    if "debug" in argvs:
        osc.setDebug()
    GUN_MODE = [[0]]
    TAB_MODE = [[0]]
    if len(argvs) > 1:
        if "local" in argvs:
            osc.setLocal()
        mode = argvs[1]
        if mode == "1":#single mode
            GUN_MODE = [[0]]
            TAB_MODE = [[0,1,2,3,4,5,6,7,8,9]]
        if mode == "12":#single 12 mode
            GUN_MODE = [[0]]
            TAB_MODE = [[0,1,2,3,4,5,6,7,8,9,10,11]]
        if mode == "2":#battle mode
            GUN_MODE = [[0],[1]]
            TAB_MODE = [[0,1,2,3,4],[5,6,7,8,9]]
        if mode == "3":#collab mode
            GUN_MODE = [[0,1]]
            TAB_MODE = [[0,1,2,3,4,5,6,7,8,9]]
        if mode == "5":#battle mode
            GUN_MODE = [[0]]
            TAB_MODE = [[0,1,2,3,4]]
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
            stage = update(count,stage,timeScale,TAB_MODE,GUN_MODE,tabState,gunState,osc,window)
            time.sleep(1/30.)
            if count % FPS == 0:
                print("["+str(count/FPS)+"]"+str(stage))
                score = calcScore(len(TAB_MODE), userDict, osc.recv)
        # action when stage changed
        if stagePre != stage:
            if stage == STAGE_COUNTDOWN:
                countdownState(tabState,gunState)
                osc.sendGunAll("/sensor",[1])
                osc.sendTabAll("/start",[])
                osc.sendAudioLevel(0)
                osc.sendAudioMode(0)
                osc.sendStartAudio()

            if stage == STAGE_LEVEL_1:
                startState(tabState,gunState)
                osc.sendAudioLevel(1)
                osc.clearRecv()

            if stage == STAGE_LEVEL_3:
                osc.sendTabAll("/level",[3])
                osc.sendAudioMode(1)

            if stage == STAGE_END:
                osc.sendTabAll("/end",[])
                osc.sendAudioLevel(0)

            if stage == STAGE_RESULT:
                score = calcScore(len(TAB_MODE), userDict, osc.recv)
                for i in range(len(TAB_MODE)):
                    for j in range(len(TAB_MODE[i])):
                        osc.sendTab("/result",[ max(1,score[i]) ],TAB_MODE[i][j])

            if stage == STAGE_RANK:
                score = calcScore(len(TAB_MODE), userDict, osc.recv)
                for i in range(len(TAB_MODE)):
                    for j in range(len(TAB_MODE[i])):
                        osc.sendTab("/resultother",[ calcRank(max(1,score[i])) ],TAB_MODE[i][j])

            if stage == STAGE_INIT:
                osc.sendTabAll("/init",[])
                osc.sendAudioMode(0)
                osc.sendAudioLevel(0)
                osc.clearRecv()
                initGunMode(osc)
                count = 0

        #item update
        for i in range(len(osc.recvItem)):
            if osc.recvItem[i][1] == 0:
                groupID = userDict[ osc.recvItem[i][0][0] ]
                print("power up!!!")
                powerGunMode(osc, GUN_MODE[groupID])
                osc.recvItem[i][1] = 1

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
        if key == ord('m'):#detect motor mode
            osc.sendGunAll("/sensor",[1])
        if key == ord('o'):#always motor on
            osc.sendGunAll("/sensor",[0])
        if key == ord('u'):#up
            osc.sendTab("/up",[6000],0)
        if key == ord('t'):#start
            osc.sendTab("/start",[],0)
        if key == ord('l'):#level mode 1
            osc.sendGunAll("/mode",[1])
        if key == ord('k'):#level mode 0
            osc.sendGunAll("/mode",[0])
        if key == ord('a'):#level mode 0
            osc.sendAudioMode(0)
        if key == ord('z'):#level mode 0
            osc.sendAudioMode(1)
    pass


def makeDictIp2User(TAB_IPS, TAB_MODE):
    out = {}
    for i in range(len(TAB_MODE)):
        for j in TAB_MODE[i]:
            out[TAB_IPS[j]] = i
    out[libOSC.LOCAL_IP] = 0
    return out

def calcRank(score):
    t = [200,400,600]
    for i, j in enumerate(t):
        if score < j:
            return i
    return len(t)

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
    score_out =[]
    for i in score:
        score_out.append(int(i/LEVEL_RATIO))
    return score_out


def initGunMode(osc):
    osc.sendGunAll("/sensor",[0])
    osc.sendGunAll("/mode",[1])
    osc.sendGunAll("/power",[60])

def powerGunMode(osc,idxs = None):
    if idxs is not None:
        for i in idxs:
            osc.sendGun("/mode",[0],i)
            osc.sendGun("/power",[100],i)
    else:
        osc.sendGunAll("/mode",[0])
        osc.sendGunAll("/power",[100])

def update(count,stage,timeScale,tabMode,gunMode,tabState,gunState,osc,window):
    #print("count", count,"stage",stage)
    if count == int(4 * FPS * timeScale):
        print("[Update] change to STAGE_LEVEL_1")
        stage = STAGE_LEVEL_1
    if count == int(20 * FPS  * timeScale):
        print("[Update] change to STAGE_LEVEL_2")
        stage = STAGE_LEVEL_2
    if count == int(23 * FPS  * timeScale):
        print("[Update] change to STAGE_LEVEL_3")
        stage = STAGE_LEVEL_3
    if count == int(33 * FPS  * timeScale):
        print("[Update] stage end")
        stage = STAGE_END
    if count == int(35 * FPS  * timeScale):
        print("[Update] stage result")
        stage = STAGE_RESULT
    if count == int(38 * FPS  * timeScale):
        print("[Update] stage rank")
        stage = STAGE_RANK
    if count == int(44 * FPS  * timeScale):
        print("[Update] initialize")
        stage = STAGE_INIT

    if stage == STAGE_LEVEL_1:
        for gIdx,tabList in enumerate(tabState):
            if random.random() > 0.5:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    if random.random() > 0.8:
                        tabList[idx] = MATO2_STATUS_OFFSET + 30*6
                        osc.sendTab("/item",[1000*6,1],tabMode[gIdx][idx])
                    else:
                        tabList[idx] = MATO1_STATUS_OFFSET + 30*6
                        osc.sendTab("/up",[1000*6],tabMode[gIdx][idx])
    if stage == STAGE_LEVEL_2:
        for gIdx,tabList in enumerate(tabState):
            if random.random() > 0.7:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    if random.random() > 0.9:
                        tabList[idx] = MATO2_STATUS_OFFSET + 30*6
                        osc.sendTab("/item",[1000*5,1],tabMode[gIdx][idx])
                    else:
                        tabList[idx] = MATO1_STATUS_OFFSET + 30*6
                        osc.sendTab("/up",[1000*5],tabMode[gIdx][idx])
    if stage == STAGE_LEVEL_3:
        for gIdx,tabList in enumerate(tabState):
            if random.random() > 0.8:
                idx = random.randint(0,len(tabList)-1)
                if tabList[idx] == 10:
                    if random.random() > 0.9:
                        tabList[idx] = MATO2_STATUS_OFFSET + 30*5
                        osc.sendTab("/item",[1000*5,1],tabMode[gIdx][idx])
                    else:
                        tabList[idx] = MATO1_STATUS_OFFSET + 30*5
                        osc.sendTab("/up",[1000*5],tabMode[gIdx][idx])
    updateState(tabState,gunState)
    #printState(tabState,gunState)
    return stage
    
if __name__=='__main__':
    argvs=sys.argv
    print(argvs)
    main(argvs)