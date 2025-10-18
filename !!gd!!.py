import pyautogui as ag
import pytesseract as pt
from time import time, sleep
from mss import mss
import matplotlib.pyplot as plt
import numpy as np
import random
from math import log, inf
import ctypes, psutil, os
from datetime import datetime


pt.pytesseract.tesseract_cmd = r'C:\Users\nicho\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

batchsize = 10
startdelay = 1.5

errors = []
results = []

ag.moveTo(1230,600)

def getpercent(display=False):

    sct = mss()
    sct_params = {'top': 40, 'left': 1647, 'width': 140, 'height': 30}
    arr = np.asarray((sct.grab(sct_params)))
    if display:
        plt.imshow(arr)
        plt.show()
    
    return (pt.image_to_string(arr,config='--psm 7'))

ag.PAUSE = 0.0
print('Loaded')

cmds = ['h','s', 'ss','sh','ms','mh','ls','lh']

p = psutil.Process(os.getpid())
p.nice(psutil.REALTIME_PRIORITY_CLASS)
ctypes.windll.kernel32.SetThreadAffinityMask(-1, 1)
ctypes.windll.winmm.timeBeginPeriod(1)
SendInput = ctypes.windll.user32.SendInput
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
MOUSEEVENTF_ABSOLUTE = 0x8000
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("mi", MOUSEINPUT)]
def C_click():
    inp = INPUT(type=0, mi=MOUSEINPUT(0,0,0,2,0,None))  # down
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    inp.mi.dwFlags = 4  # up
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))



def execute(delays, startpoint = 0):
    delays = delays[startpoint:]
    print('running:')
    print(delays[-10:])
    sdelays = [startdelay] + delays


    ag.moveTo(1230,600)
    
    starttime = time()
    hasmoved = False
    holding = False
    spamming = False
    cmdlength = None
    t1 = 'pi'
    r1delay = 0
    for i in sdelays:
        s = ''
        if isinstance(i,str):
            if len(i) == 1:
                cmdlength = None
            elif i[0] == 's':
                cmdlength = 0
            elif i[0] == 'm':
                cmdlength = 0.1
            elif i[0] == 'l':
                cmdlength = 0.5
            if  i[-1] == 's':
                spamming = True
            elif  i[-1] == 'h':
                holding = True
                if len(i) == 1:
                    ag.mouseDown()
            continue

        while time()-(starttime+r1delay) < i:
            if spamming and cmdlength is None:
                C_click()
                sleep(0.001)
        if cmdlength is not None:
            if cmdlength == 0:
                C_click()
            else:
                if holding:
                    ag.mouseDown()
                while time()-(starttime+r1delay) < i + cmdlength:
                    if spamming:
                        C_click()
                        sleep(0.001)
                if holding:
                    ag.mouseUp()

        elif not holding and not spamming:
            s = 'normal'
            if not hasmoved and i != startdelay:
                ag.moveTo(1230,400)
            t1 = time()-starttime-i
            C_click()
            t2 = time()-starttime-i
        elif holding:
            s = 'holding'
            ag.mouseUp()
            holding = False
        elif spamming:
            s = 'spamming'
            spamming = False
        else:
            raise Exception("Improper state. No idea how you managed to do that.")
        delay = time()-starttime-i-r1delay
        if startdelay == i:
            r1delay = delay
            print('R1delay:',r1delay)
        errors.append(log(max(0.00001,delay)))
        if delay > 0.005:
            print(s+'. delay1',t1,'delay2',t2,' delay:',round(delay,5),'on',i)
        cmdlength = None
    print('Finished!')
    sleep(1)
    p = 0
    count = 0
    while not isreasonable(p):
        p0 = getpercent().strip().split('%')[0].replace(')','').replace("'",'').replace('.','').replace('|','')
        outp = ''
        for i in p0:
            if i in '1234567890':
                outp += i
        p = int('0' + outp)
        count += 1
        if count > 10:
            print('\n\nGLITCH\n\n')
            #getpercent(True)
            break
    print('Percent = ',p)
    sleep(2)        
    print('(acquired in',time()-starttime,'seconds)')
    try:
        return p
    except:
        return 0

def isreasonable(value):
    return value > 10 and value < 100*100+100

sep = '&&&'
def save(delays, lvlname):
    file = open('#offiles.txt','r')
    gindex = None
    lines = file.read().split('\n')
    for i in range(len(lines)):
        if lines[i].split(sep)[0] == lvlname:
            gindex = int(lines[i].split(sep)[1]) + 1
            lines[i] = lines[i].split(sep)[0]+sep + str(gindex)+sep+str(startdelay)
    if not gindex:
        gindex = 1
        lines.append(lvlname+' 1 '+str(gindex))
    file.close()
    
    fname = lvlname+str(gindex-1)+'.txt'
    file = open(fname,'w+')
    file.write(' '.join(map(str,delays)))
    file.close()
    print(lines)
    txt = '\n'.join(lines)
    file = open('#offiles.txt','w')
    file.write(txt)
    file.close()

def load(lvlname):
    global startdelay
    file = open('#offiles.txt','r')
    lines = file.read().split('\n')
    gindex = 0
    for i in lines:
        if i.split(sep)[0] == lvlname:
            gindex = int(i.split(sep)[1])
            startdelay = float(i.split(sep)[2])
    file.close()
    
    fname = lvlname+str(gindex-1)+'.txt'
    print(fname)
    lastfile = open(fname).read().split(' ')
    oplist = []
    for i in lastfile:
        try:
            oplist += [float(i)]
        except:
            oplist += [i]
    return oplist

def logbest(score):
    file = open('$$LOGS$$.txt','a+')
    time = str(datetime.now())
    string = time + ': '+str(score)  + '%\n'
    file.write(string)
    file.close()

def addrand(delaylist):
    cmded = False
    if random.randint(0,2) == 1:
        delaylist.append(random.choice(cmds[0:2]))
        cmded = True
    if cmded:
        chg = round(abs(random.gauss(0,0.6)),2)
    else:
        chg = round(abs(random.gauss(0,1)),2)
    if len(delaylist) > 0:
        if delaylist[-1] in cmds:
            if len(delaylist) > 1:
                delaylist.append(delaylist[-2] + chg)
            else:
                delaylist.append(startdelay+chg)
                
        else:
            delaylist.append(delaylist[-1] + chg)
    else:
        delaylist.append(startdelay+chg)


def mutate(delaylist):
    dchance = 0
    if random.randint(0,1) != 0:
        addrand(delaylist)    
    else:
        dchance += 1
    for i in range(len(delaylist)):
        if delaylist[-i-1] in cmds:
            continue
        if random.randint(0,int(4**(i+1-dchance))) == 1:
            delaylist[-i-1] += round((random.gauss(0,0.4))/2,2)
        if i == 0 and random.randint(0,8) == dchance-1:
            delaylist.pop(-1)
            if delaylist[-1] in cmds:
                delaylist.pop(-1)
            addrand(delaylist)
            return
    for i in range(len(delaylist)):
        if delaylist[i] not in cmds:
            if random.randint(0, 2*len(delaylist)) == 1:
                delaylist[i] += 0.01 * random.randint(-1,1)
                print('miniapplied',i)

    toremove = []
    for i in range(1,len(delaylist)):
        if delaylist[i] in cmds:
            continue
        delaylist[i] = round(delaylist[i],2)
        if delaylist[i-1] in cmds:
            if i > 1 and delaylist[i-2] > delaylist[i]:
                toremove.append(i-1)
                toremove.append(i)
        elif delaylist[i-1] > delaylist[i]:
            toremove.append(i)
    toremove.sort()
    for i in range(len(toremove)):
        delaylist.pop(toremove[i]-i)

        
def getscore(time, cmds):
    if cmds == []:
        score = time
    else:
        score = time-7*cmds[-1]
        if cmds[-1] > time * 1.5:
            score -= 3
    return score

def checkinconsistency(delays, highscore = None):
    print('Checking inconsistency for',delays)
    if highscore == 1492:
        return (True, 992)
    if highscore:
        score1 = highscore
    else:
        score1 = execute(delays)
    score2 = execute(delays)
    score3 = execute(delays)
    mini = min(score1,score2,score3)
    maxi = max(score1,score2,score3)
    if maxi - mini > 10:
        return (True, mini)
    else:
        return (False, mini)

def findcommandfor(delays, point):
    guess = point/100
    for i in delays:
        if i in cmds:
            continue
        if i > guess:
            guess = delays.index(i)
            break
    else:
        guess = len(delays)-3
    guessmin = 0
    guessmax = len(delays)-1
    while True:
        reducedelays = delays[0:guess]
        result = execute(reducedelays)
        print('commands up to',guess,'resulted in', result)
        if result > point - 5:
            #guess too high
            guessmax = guess
            guess = int(guessmin + 3/4 * (guessmax - guessmin))
        else:
            guessmin = guess
            guess = int(guessmin + 1/2*(guessmax - guessmin))
        print('min:',guessmin,'max', guessmax,'midpoint', guess)

        if guessmin + 1 >= guessmax:
            break
    return guess

def tryfixcommand(delays, guess):
    for offset in [0,-1,1]:
        if delays[guess + offset] in cmds:
            tochange = guess + {-1:-2,0:2,1:2}[offset]
        else:
            tochange = guess + offset
        plusdelays = delays.copy()
        plusdelays[tochange] += 0.03

        minusdelays = delays.copy()
        minusdelays[tochange] -= 0.03
        inconsistent, stoppointp = checkinconsistency(plusdelays)
        if not inconsistent:
            inconsistent, stoppointm = checkinconsistency(minusdelays)
            if not inconsistent and abs(stoppointm - stoppointp) > 10:
                if stoppointp > stoppointm:
                    return plusdelays
                else:
                    return minusdelays


def fixinconsistentcommand(delays, highscore):
    inconsistent, deathpoint = checkinconsistency(delays, highscore)
    if not inconsistent:
        return
    print('Inconsistency detected')
    guess = findcommandfor(delays, deathpoint)

    print(f'#{guess} IS THE ISSUE! ({delays[guess]})')

    result =  tryfixcommand(delays, guess)
    if result:
        return result



def replicatewinners(batch, scores):
    print(scores)
    batchscores = []
    for i in range(len(batch)):
        if batch[i] == []:
            score = scores[i]
        else:
            score = scores[i]-0.001*batch[i][-1]
            if batch[i][-1] > scores[i] * 1.5:
                score -= 3
        batchscores.append((score, batch[i]))
    batchscores.sort()
    batchscores = batchscores[::-1]
    print(scores)
    outputlist = [batchscores[0][1].copy()] #keep a copy of the very best
    weights = [5,3,1]
    assert sum(weights) == batchsize-1
    for c in range(len(weights)):
        for j in range(weights[c]):
            toadd = batchscores[c][1].copy()
            mutate(toadd)
            outputlist.append(toadd)
    return outputlist


def runbatches(prevbest):
    scores = list(range(10))
    batch = [prevbest.copy() for i in range(batchsize)]
    batch = replicatewinners(batch, scores)
    assert len(batch) == batchsize
    print(batch)
    batchnum = 0
    while True:
        batchnum += 1
        print('Starting batch #'+str(batchnum))
        scores = []
        for current in batch:
            p = execute(current)
            scores.append(p)
        batch = replicatewinners(batch, scores)
        save(batch[0])



def runcont(prevbest):
    bestp = execute(prevbest)
    bestscore = getscore(bestp, prevbest)
    print('Score to beat:', bestscore)
    counter = 0
    while True:
        scoreboost = 0
        counter += 1
        if counter % 120 == 100:
            print('Fixing inconsistencies...')
            current = fixinconsistentcommand(prevbest, bestp)
            scoreboost = 10
            if not current:
                current = prevbest.copy()
                mutate(current)
                scoreboost = 0
        else: 
            current = prevbest.copy()
            mutate(current)
        if current == prevbest:
            continue
        p = execute(current)
        if len(str(p)) > len(str(bestp)) and str(p)[0] == str(bestp)[0] and '1' in str(p):
            p = int(str(p)[0] + str(p)[2:]  )   
        results.append(p)       
        score = getscore(p, current) + scoreboost
        print('Score:',score)
        if score > bestscore+1 and score < bestscore + 1000:
            print('May be higher, rematching...\n')
            score2 = execute(current)
            bestp = execute(prevbest)
            if getscore(score2, current) + scoreboost > getscore(bestp, prevbest):
                print('\n NEW BEST!!!\n')
                logbest(score2/100)
                prevbest= current
                if abs(score2 - bestp) < abs(score - bestp):
                    bestscore = score2
                else:
                    prevbest = current
                bestscore = score
                save(current, level)

level = input('Which level?').lower().strip()

try:
    prevbest = load(level)
except FileNotFoundError:
    print('No file found')
    prevbest = []
#print(fixinconsistentcommand(prevbest[0:30], 1492))
#plt.hist(errors)
#plt.show()
#print('\n\n',findcommandfor(prevbest,1477),'\n\n')
#execute(prevbest)
#quit()

try:
    runcont(prevbest)
except:
    plt.hist(errors)
    plt.show()
    plt.hist(results,bins=int(max(results)/100))
    plt.show()

