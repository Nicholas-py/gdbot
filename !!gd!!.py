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
    sct_params = {'top': 40, 'left': 1647, 'width': 180, 'height': 35}
    arr = np.asarray((sct.grab(sct_params)))
    if display:
        plt.imshow(arr)
        plt.show()
    
    return (pt.image_to_string(arr,config='--psm 7'))

ag.PAUSE = 0.0
print('Loaded')

cmds = ['h','s','ms','ls', 'ss','sh','mh','xh','lh']
cmdsinuse = cmds[4:]

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
                cmdlength = 0.3
            elif i[0] == 'x':
                cmdlength = 0.2
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
        elif spamming:
            s = 'spamming'
        else:
            raise Exception("Improper state. No idea how you managed to do that.")
        delay = time()-starttime-i-r1delay
        if startdelay == i:
            r1delay = delay
            print('R1delay:',r1delay)
        errors.append(log(max(0.00001,delay)))
        if delay > 0.005:
            print(s+'. delay1',round(t1,3),'delay2',round(t2,4),' delay:',round(delay,5),'on',i)
        cmdlength = None
        spamming = False
        holding = False
    print('Finished!')
    sleep(1)
    p = stablepercent()
    print('Percent = ',p)
    sleep(2)
    p2 = stablepercent()    
    results.append(p2)       
    print('(acquired in',time()-starttime,'seconds)')
    return p, p2

def stablepercent():
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
    return p

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
        lines.append(lvlname+sep+'1'+sep+str(gindex))
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
    delaylist.append(random.choice(cmdsinuse[2:]))
    chg = round(abs(random.gauss(0,0.8)),2)
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
        if random.randint(0,3) == 0:
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

def isfirstargbetter(score1, cmds1, score2, cmds2):
    if abs(score1[1] - score2[1] > 1000):
        return False
    if abs(score1[1] - score2[1]) > 5:
        return score1[1] > score2[1]
    elif abs(score1[0] - score2[0]) > 5:
        return score1[0] > score2[0]
    else:
        print('Tiebreak - last arg',cmds1[-1] < cmds2[-1])
        return cmds1[-1] < cmds2[-1]


def getscore(time, cmds):
    if cmds == []:
        score = time
    else:
        score = time[0]-7*cmds[-1]
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
        score1 = execute(delays)[1]
    score2 = execute(delays)[1]
    score3 = execute(delays)[1]
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
        result = execute(reducedelays)[0]
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
    #bestscore = getscore(bestp, prevbest)
    print('Score to beat:', bestp)
    counter = 0
    while True:
        counter += 1
        current = prevbest.copy()
        mutate(current)

        if current == prevbest:
            continue

        p = execute(current)
        #score = getscore(p, current)
        print('Score:',p)

        if isfirstargbetter(p, current, bestp, prevbest):
            print('May be higher, rematching...\n')
            score2 = execute(current)
            bestp = execute(prevbest)

            if isfirstargbetter(score2, current, bestp, prevbest):
                print('\n NEW BEST!!!\n')
                logbest(score2[1]/100)
                prevbest = current
                if abs(score2[1] - bestp[1]) < abs(p[1] - bestp[1]):
                    bestp = score2
                else:
                    bestp = p
                save(current, level)

#execute([ 'h', 11.84, 'mh', 12.28, 'xh', 12.37, 'lh', 13.13, 'xh', 13.15])

#execute(['ss',1,'mh',2,'ms',3,'lh',4,'ls',5])
execute([2.32, 2.34, 3.07, 's', 3.25, 'h', 3.75, 4.26, 's', 4.81, 5.11, 5.17, 's', 5.38, 5.98, 6.7, 's', 8.1, 'h', 8.51, 9.22, 's', 
       9.71, 10.29, 10.98, 's', 11.55, 's', 11.86, 12.26, 12.34, 13.21, 'h', 13.62, 14.4, 's', 15.3, 's', 15.72, 16.46, 17.13, 17.95,
         'h', 18.59, 19.28, 20.33, 's', 20.88, 'h', 21.32, 21.39, 'h', 21.54, 's', 22.04,
         's', 22.27, 's', 23.38, 24.12, 24.64, 25.7, 's', 26.23, 'h', 27.3, 28.05, 29.31, 30.28, 31.3, 
         31.89, 32.51, 's', 33.34, 33.73, 34.48, 'h', 35.15, 35.77, 'h', 36.66, 36.97, 's', 37.32, 
         38.07, 'h', 38.63, 38.89, 39.6, 'h', 40.69, 41.41, 's', 42.91, 's', 43.82, 's', 44.38,'h', 45.13,
         45.28, 46.0, 46.86,90, 47.62, 48.1, 49.14, 's', 49.77, 50.88, 'h', 51.3, 51.6,
          'h', 51.9, 52.1, 'h', 52.42, 'h', 53.0, 53.39, 's', 53.95, 54.44, 'h', 54.95, 's', 55.71, 56.26,
      'h', 56.73, 'h', 57.88, 'h', 58.39,
   's', 59.85, 's', 60.95, 's', 61.17, 61.45, 'h', 61.84, 'mh', 62.28, 'xh', 62.37, 'xh', 63.1, 'xh', 63.15])#, 'dry out')


level = input('Which level?').lower().strip()
try:
    prevbest = load(level)
except FileNotFoundError:
    print('No file found')
    prevbest = []

#while True:
 #   execute(prevbest)

try:
    runcont(prevbest)
except:
    plt.hist(errors)
    plt.show()
    plt.hist(results,bins=100)
    plt.show()
    raise Exception('EXITING')

