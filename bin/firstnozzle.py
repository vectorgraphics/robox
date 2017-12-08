#!/usr/bin/env python
import fileinput
import sys
import re

t0first=len(sys.argv) < 2 or sys.argv[1] != "1"

t0firstLayers=sys.argv[2:]

if len(t0firstLayers) == 0:
    t0firstLayers=map(str,range(0,1000))
#    t0firstLayers=["0"]

numeric="([-+]?(?:(?: \d* \. \d+ )|(?: \d+ \.? )))"
rX=re.compile("X"+numeric,re.VERBOSE)
rY=re.compile("Y"+numeric,re.VERBOSE)
rZ=re.compile("Z"+numeric,re.VERBOSE)
rF=re.compile("F"+numeric,re.VERBOSE)
rT=re.compile("T"+numeric,re.VERBOSE)
rD=re.compile("D"+numeric,re.VERBOSE)
rE=re.compile("E"+numeric,re.VERBOSE)
rL=re.compile(";LAYER:"+numeric,re.VERBOSE)

L=-1
T=0
X=0
Y=0
T0=[]
T1=[]
lX=[]
lY=[]
lZ=[]
lastT=-1
L=-1
B=0
Heater="M103"
finish=False
replenishD="G1 B1 F150 D0.30\n"
replenishE="G1 B1 F150 E0.30\n"
#primesuffixD="M109\nG36 D0.0 F1000\n"
#primesuffixE="M109\nG36 E0.0 F1000\n"

buffer=[]
prologue=[]
start=0

for line in fileinput.input("-"):
    if finish:
        prologue.append(line)
        continue
    lT=rT.findall(line)
    if len(lT) > 0:
        T=int(lT[0])    
    lZ=rZ.findall(line)
    lX=rX.findall(line)
    lY=rY.findall(line)
    if len(lX) > 0:
        X=float(lX[0])
    if len(lY) > 0:
        Y=float(lY[0])
    reorder=L >= 0
    if reorder and (re.match(Heater,line) or re.match("M140",line)):
        line=""
    if re.match("; Post print gcode",line):
        finish=True
        reorder=False
    if reorder and not (re.match(";LAYER:",line) or len(lZ) > 0): 
        if T == 0 :
            lD=rD.findall(line)
            if T != lastT:
                T0.append("G0 B0\n")
                T0.append("T0 F12000 X"+str(X)+" Y"+str(Y)+"\n")
                B=0
                lastT=T
            if B == 0:
                if len(lD) > 0:
                    B=1
                    T0.append(replenishD)
            T0.append(line)
        elif T == 1:
            if T != lastT:
                T1.append("G0 B0\n")
                T1.append("T1 F12000 X"+str(X)+" Y"+str(Y)+"\n")
                B=0
                lastT=T
            if B == 0:
                lE=rE.findall(line)
                if len(lE) > 0:
                    B=1
                    T1.append(replenishE)
            T1.append(line)
        else:
            buffer.append(line)
    else:
        if len(T0) > 0 and t0first:
            for l in T0:
                buffer.append(l)
            T0=[]

        if len(T1) > 0:
            for l in T1:
                buffer.append(l)
            T1=[]

        if len(T0) > 0 and not t0first:
            for l in T0:
                buffer.append(l)
            T0=[]

        lL=rL.findall(line)
        if len(lL) > 0:
            L=int(lL[0])
            if L == 0 and start == 0:
                start=len(buffer)
            if L == 1:
                Heater="M104"
            if reorder:
                buffer.append("G0 B0\n")
                B=0
        if L >= 0 and B == 0:
            lD=rD.findall(line)
            if len(lD) > 0:
                T=0
                B=1
                buffer.append("T0\n"+replenishD)
            lE=rE.findall(line)
            if len(lE) > 0:
                T=1
                B=1
                buffer.append("T1\n"+replenishE)
        buffer.append(line)
        lastT=-1

Heater="M103"
count=start
count0=0
count1=0
pretime=100
posttime=100
primetime=pretime+posttime;
lastT=-1
T=lastT
time=0
X0=0
Y0=0
F=0
index=[0]*start

from math import sqrt
from bisect import bisect_left

while count < len(buffer):
    lF=rF.findall(line)
    lX=rX.findall(line)
    lY=rY.findall(line)
    if len(lF) > 0:
        F=float(lF[0])/60
        if len(lX) > 0:
            X=float(lX[0])
        if len(lY) > 0:
            Y=float(lY[0])
        dist=sqrt((X-X0)**2+(Y-Y0)**2)
        time += dist/F
    index.append(time)
    X0=X
    Y0=Y
    line=buffer[count]
    lL=rL.findall(line)
    if len(lL) > 0:
        L=int(lL[0])
        if L == 1:
            Heater="M104"
            buffer.insert(count,"M140\n")
            index.insert(count,index[count])
            count += 1
    lT=rT.findall(line)
    if len(lT) > 0:
        T=int(lT[0])
    if T == 0:
        if T != lastT:
            lastT=T
            if time-index[count1] > posttime:
                buffer.insert(count1,Heater+" S0\n")
                index.insert(count1,index[count1])
                count += 1
#                if L == 0 and time-index[count1] > primetime:
#                    buffer.insert(count+1,primesuffixD)
#                    index.insert(count,index[count])
#                    count += 1
            i=max(count1+1,bisect_left(index,time-pretime))
            if i > start and i < len(index):
                buffer.insert(i,Heater+" S\n")
                index.insert(i,index[i])
                count += 1
            count0=count
    elif T == 1:
        if T != lastT:
            lastT=T
            if time-index[count0] > posttime:
                buffer.insert(count0,Heater+" T0\n")
                index.insert(count0,index[count0])
                count += 1
#                if L == 0 and time-index[count0] > primetime:
#                    buffer.insert(count+1,primesuffixE)
#                    index.insert(count,index[count])
#                    count += 1
            i=max(count0+1,bisect_left(index,time-pretime))
            if i > start and i < len(index):
                buffer.insert(i,Heater+" T\n")
                index.insert(i,index[i])
                count += 1
            count1=count
    count += 1

if T == 1 and time-index[count1] > pretime:
    buffer.insert(count1,Heater+" S0\n")
    index.insert(count1,index[count1])

if T == 0 and time-index[count0] > pretime:
   buffer.insert(count0,Heater+" T0\n")
   index.insert(count0,index[count0])
    
for line in buffer:
    sys.stdout.write(line)

for line in prologue:
    sys.stdout.write(line)

sys.stdout.flush()
