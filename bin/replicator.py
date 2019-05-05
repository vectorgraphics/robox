#!/usr/bin/env python
import fileinput
import sys
import re

nx0=0
ny0=0

file=sys.argv[1]

if(len(sys.argv) > 2):
    nx0=int(sys.argv[2])
if(len(sys.argv) > 3):
    ny0=int(sys.argv[3])

numeric="([-+]?(?:(?: \d* \. \d+ )|(?: \d+ \.? )))"
rB=re.compile("B"+numeric,re.VERBOSE)
rD=re.compile("D"+numeric,re.VERBOSE)
rE=re.compile("E"+numeric,re.VERBOSE)
rX=re.compile("X"+numeric,re.VERBOSE)
rY=re.compile("Y"+numeric,re.VERBOSE)
rZ=re.compile("Z"+numeric,re.VERBOSE)
rT=re.compile("T"+numeric,re.VERBOSE)
rL=re.compile(";LAYER:"+numeric,re.VERBOSE)

buffer=[]
prologue=[]

Length=205

#Width=150
#Width=148
Width=144 # Avoid cool back edge 
ygap=10

Xmin=Length
Ymin=Width

Xmax=0
Ymax=0

X0=0
Y0=0

finish=False

L=-1
for line in fileinput.input(file):
    if re.match("; Post print gcode",line):
        finish=True
    if finish:
        prologue.append(line)
        continue
    lL=rL.findall(line)
    if len(lL) > 0:
        L=int(lL[0])
        if(L < 0):
            print "Rafts are not supported!"
            exit()
    if(L < 0):
        sys.stdout.write(line)
        continue
    buffer.append(line)
    lX=rX.findall(line)
    lY=rY.findall(line)
    if len(lX) > 0:
        X=float(lX[0])
        Xmin=min(Xmin,X)
        Xmax=max(Xmax,X)
    if len(lY) > 0:
        Y=float(lY[0])
        Ymin=min(Ymin,Y)
        Ymax=max(Ymax,Y)

L=-1
Z=0
T=0

for line in buffer:
    lX=rX.findall(line)
    lY=rY.findall(line)
    lZ=rZ.findall(line)
    lT=rT.findall(line)
    if len(lX) > 0:
        X=float(lX[0])
    if len(lY) > 0:
        Y=float(lY[0])
    if len(lZ) > 0:
        Z=float(lZ[0])
    if len(lT) > 0:
        T=int(lT[0])    
    if T == 0:
        offset=0
    else:
        offset=15
    if Z < 10:
        X0=max(X0,X+12+offset)
        Y0=max(Y0,Y+14)
    else:
        if(Ymax-Ymin > 45):
            offset += 2
        X0=max(X0,X+19+offset)
        Y0=max(Y0,Y+min(31,21+10*(Z-10)/20))

x=Xmax-Xmin
y=Ymax-Ymin

mx=X0-Xmax
my=Y0-Ymax

X=Length
Y=Width-ygap
    
nx=int((X+mx)/(x+mx))
ny=int((Y+my)/(y+my))

if(nx0 > 0):
    nx=min(nx,nx0)
if(ny0 > 0):
    ny=min(ny,ny0)

xoffset=(X-nx*x-(nx-1)*mx)/2
yoffset=ygap+(Y-ny*y-(ny-1)*my)/2

T=0
lastT=0

for j in range(ny):
    y0=yoffset+j*(y+my)
    for i in range(nx):
        x0=xoffset+i*(x+mx)
        L=-1
        for line in buffer:
            lL=rL.findall(line)
            lT=rT.findall(line)
            if len(lT) > 0:
                T=int(lT[0])
                if L == 0:
                    lastT=T
            if len(lL) > 0:
                L=int(lL[0])
                if L == 1:
                    break
                if L == 0 and (i > 0 or j > 0):
                    sys.stdout.write("G1 B0\n")
            lX=rX.findall(line)
            lY=rY.findall(line)
            if len(lX) > 0:
                line=line.replace("X"+lX[0],"X"+str(float(lX[0])-Xmin+x0))
            if len(lY) > 0:
                line=line.replace("Y"+lY[0],"Y"+str(float(lY[0])-Ymin+y0))
            if not (re.match("M104",line) or re.match("M140",line)) or (j == ny-1 and i == nx-1):
                sys.stdout.write(line)

B=0
reopen=""

for j in range(ny):
    y0=yoffset+j*(y+my)
    for i in range(nx):
        x0=xoffset+i*(x+mx)
        L=-1
        for line in buffer:
            lB=rB.findall(line)
            if len(lB) > 0:
                B=float(lB[0])
            lL=rL.findall(line)
            if len(lL) > 0:
                L=int(lL[0])
                if L == 1:
                    sys.stdout.write("T"+str(lastT)+"\n")
                    sys.stdout.write(line)
                    sys.stdout.write("G0 B0\nG1 F12000 Y"+str(y0)+"\nG1 F12000 X"+str(x0)+"\n")
                    reopen="G0 B"+str(B)+"\n"
                    continue
            if L >= 1:
                lX=rX.findall(line)
                lY=rY.findall(line)
                lZ=rZ.findall(line)
                if len(lX) > 0:
                    line=line.replace("X"+lX[0],"X"+str(float(lX[0])-Xmin+x0))
                if len(lY) > 0:
                    line=line.replace("Y"+lY[0],"Y"+str(float(lY[0])-Ymin+y0))
                sys.stdout.write(line)
                if len(lZ) > 0 and reopen != "":
                    sys.stdout.write(reopen)
                    reopen=""

for line in prologue:
    sys.stdout.write(line)

sys.stdout.flush()

# Now pipe into firstnozzle
