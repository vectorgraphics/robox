#!/usr/bin/env python3
import fileinput
import sys
import re
import math
import os
from pathlib import Path

numeric="([-+]?(?:(?: \d* \. \d+ )|(?: \d+ \.? )))"
rX=re.compile("X"+numeric,re.VERBOSE)
rY=re.compile("Y"+numeric,re.VERBOSE)
rZ=re.compile("Z"+numeric,re.VERBOSE)
rF=re.compile("F"+numeric,re.VERBOSE)
rB=re.compile("B"+numeric,re.VERBOSE)
rD=re.compile("D"+numeric,re.VERBOSE)
rE=re.compile("E"+numeric,re.VERBOSE)
rT=re.compile("T"+numeric,re.VERBOSE)
rL=re.compile(";LAYER:"+numeric,re.VERBOSE)
skin=False
fill=False
inner=False
outer=False
support=False

digits=5
distance=5
B=""
F=""
X=""
Y=""
T=0
Z=0
X0=""
Y0=""
X1=""
Y1=""
lastZ=0
L=-1
lastextrusion=""
replenishD=0
replenishE=0
#interface=False
#lastinterface=False
incr=[0,0]
current=[]
previous=[]

epsilon=5e-4
threshold=1.0/3.0
e=1 # extrusion error

#zdelta=-0.13
zdelta=0;

#PETG=[False,False]
PETG=[False,True]
#PETG=[True,False]
#PETG=[True,True]

#TODO: simplify code

if(PETG[0] == True):
  primeDLength=8
#  firstDfactor=1.1
  firstDfactor=1.0
#  incr[0]=0.04
else:
  primeDLength=0
  firstDfactor=1.0

if(PETG[1] == True):
  primeELength=8
#  firstEfactor=1.1
  firstEfactor=1.0
#  incr[1]=0.04
else:
  primeELength=0
  firstEfactor=1.0

path=Path(os.path.expanduser("~/map.dat"));
mapping=path.is_file()

if mapping:
  file=open(path,"r")
  x=[float(a) for a in file.readline().split()]
  y=[float(a) for a in file.readline().split()]
  z=[[float(a) for a in line.split()] for line in file]

  xm=x[0]
  ym=y[0]
  dx=x[1]-xm
  dy=y[1]-ym
  nx=len(x)-1
  ny=len(y)-1
  
def height0(x,y):
  if(x < xm):
    x=xm
  if(y < ym):
    y=ym
  i=int((x-xm)/dx)
  j=int((y-ym)/dy)
  x=(x-xm-i*dx)/dx
  y=(y-ym-j*dy)/dy
  if(i >= nx):
    i=nx-1
    x=1
  if(j >= ny):
    j=ny-1
    y=1
  return z[i][j]*(1-x)*(1-y)+z[i+1][j]*x*(1-y)+z[i][j+1]*(1-x)*y+z[i+1][j+1]*x*y

if mapping:
  xlevel=(height0(190,75)-height0(20,75))/2-zdelta;

Nx=2
Xm=20
Dx=85.0

def height(x,y):
  x0=x
  if x0 < 20:
    x0=20
  i=int((x0-Xm)/Dx)
  x0=(x0-Xm-i*Dx)/Dx
  if(i >= Nx):
    i=Nx-1
    x0=1
  xi=Xm+i*Dx
  ylevel0=(height0(xi,130)-height0(xi,20))/2
  ylevel1=(height0(xi+Dx,130)-height0(xi+Dx,20))/2
  ylevel=ylevel0*(1-x0)+ylevel1*x0
  return height0(x,y)-xlevel*(x-105)/(190-105)-ylevel*(y-75)/(130-75)

# Return true iff middle portion of line segment PQ intersects with pq.
def intersectmid(Px,Py,Qx,Qy,px,py,qx,qy):
  Dx=Qx-Px
  Dy=Qy-Py
  dx=qx-px
  dy=qy-py
  vx=Px-px
  vy=Py-py
  det=Dy*dx-Dx*dy
  if abs(det) <= epsilon*max(Px,Py,Qx,Qy)*max(px,py,qx,qy):
# Find distance between lines    
    denom=Dx*Dx+Dy*Dy
    if denom == 0:
      return True
    dot=(vx*Dx+vy*Dy)/denom
    vx -= dot*Dx
    vy -= dot*Dy
    midx=0.5*(Px+Qx)
    midy=0.5*(Py+Qy)
    return vx*vx+vy*vy <= e*e and midx >= min(px,qx)-e and midx <= max(px,qx)+e and midy >= min(py,qy)-e and midy <= max(py,qy)+e
  t=vx*dy-vy*dx
  s=vy*Dx+vx*Dy
  return t/det >= threshold and t/det <= 1-threshold and s/det >= 0 and s/det <= 1

L=-1
primeD=0
primeE=0
queue=""

for line in fileinput.input():
    lX=rX.findall(line)
    lY=rY.findall(line)
    lZ=rZ.findall(line)
    if len(lX) > 0:
        X=lX[0]
    if len(lY) > 0:
        Y=lY[0]
    if len(lZ) > 0:
      Z=float(lZ[0])
    lL=rL.findall(line)
    if len(lL) > 0:
        L=int(lL[0])
#        lastinterface=interface
#        interface=False
    if line[0:6] == ";TYPE:":
        skin=re.match(";TYPE:SKIN",line)
        fill=re.match(";TYPE:FILL",line)
        inner=re.match(";TYPE:WALL-INNER",line)
        outer=re.match(";TYPE:WALL-OUTER",line)
        support=re.match(";TYPE:SUPPORT",line)
    lF=rF.findall(line)
    lT=rT.findall(line)
    if len(lT) > 0:
      T=int(lT[0])
    if mapping and L == 0 and len(lX) > 0 and len(lY) > 0:
      line=line.replace("Y"+Y,"Y"+Y+" Z"+str(round(Z+height(float(X),float(Y)),3)))
    if L > 0 and len(lZ) > 0:
        line=line.replace("Z"+lZ[0],"Z"+str(Z+incr[T]))
        if(Z != lastZ):
            if(Z > lastZ):
                previous=current
            else:
                previous=[]
            current=[]
            lastZ=Z
#    if support:
#        interface=True
    lD=rD.findall(line)
    lE=rE.findall(line)
    petg=PETG[T]
    if re.match("G1",line) and len(lF) > 0 and lF[0] != "12000":
#        if lastinterface and petg and not support:
#            line=line.replace(fs,"F"+str(min(f,25*60)))
        x=float(X)
        x0=float(X0)
        y=float(Y)
        y0=float(Y0)
        short=(x-x0)**2+(y-y0)**2 <= distance*distance
        f0=lF[0]
        fs="F"+f0
        f=int(f0)
        if petg and (len(lD) > 0 or len(lE) > 0):
            current.append([x0,y0,x,y])
            if len(previous) > 0:
                supported=False
                for Line in previous:
                    if intersectmid(x0,y0,x,y,Line[0],Line[1],Line[2],Line[3]):
                        supported=True
                        break
                if not (supported or short):
                    line=line.replace(fs,"F"+str(min(f,1200)))
                    line=line.replace("\n","; Overhang detected in L="+str(L)+" from X"+X0+" Y"+Y0+"\n")
        if L == 0:
          if petg:
            line=line.replace(fs,"F"+str(min(f,6*60)))
          else:
            if outer:
              line=line.replace(fs,"F"+str(min(f,12*60)))
            elif inner:
              line=line.replace(fs,"F"+str(min(f,8*60)))
        elif L == 1:
          if petg:
            line=line.replace(fs,"F"+str(min(f,21*60)))
        elif skin:
          if petg:
            if short:
              line=line.replace(fs,"F"+str(min(f,14*60)))
            else:
              line=line.replace(fs,"F"+str(min(f,30*60)))
          else:
#            line=line.replace(fs,"F"+str(min(f,40*60)))
            line=line.replace(fs,"F"+str(min(f,30*60)))
        elif short:
          if petg:
            line=line.replace(fs,"F"+str(min(f,20*60)))
          else:
            line=line.replace(fs,"F"+str(min(f,40*60)))
        elif petg:
          if inner or outer:
            line=line.replace(fs,"F"+str(min(f,20*60)))
          elif fill:
            line=line.replace(fs,"F"+str(min(f,73*60)))

    lB=rB.findall(line)
    if re.match("G1 [^B]*B1",line):
        sys.stdout.write("G0 B1\n")
        if len(lE) > 0:
            replenishE=float(lE[0])
        elif len(lD) > 0:
            replenishD=float(lD[0])
    else:
        if len(lE) > 0:
          if L == 0 and skin:
            old=lE[0]
            lE[0]=str(round(firstEfactor*float(lE[0]),digits))
            line=line.replace("E"+old,"E"+lE[0])
          replenishD=0
          primeD=0
          E=float(lE[0])
          if replenishE > 0:
            E += replenishE
            line=line.replace("E"+lE[0],"E"+str(round(E,digits)))
            replenishE=0
            if L == 0:
              primeE=primeELength
          if L == 0 and primeE > 0:
            line=line.replace(fs,"F"+str(min(f,480)))
            primeE -= min(primeE,E)
        if len(lD) > 0:
          if L == 0 and skin:
            old=lD[0]
            lD[0]=str(round(firstDfactor*float(lD[0]),digits))
            line=line.replace("D"+old,"D"+lD[0])
          replenishE=0
          primeE=0
          D=float(lD[0])
          if replenishD > 0:
            D += replenishD
            line=line.replace("D"+lD[0],"D"+str(round(D,digits)))
            replenishD=0
            if L == 0:
              primeD=primeDLength
          if L == 0 and primeD > 0:
            line=line.replace(fs,"F"+str(min(f,480)))
            primeD -= min(primeD,D)
        sys.stdout.write(line)
        if L >= 0 and line == "G0 B0\n" and float(B) != 0:
            line="G1 F"+F+" X"+X+" Y"+Y+" B0\n"
            X0=X1
            Y0=Y1
        if re.match("G1 [^B]*B",line) and len(lB) > 0 and float(lB[0]) == 0 and float(B) != 0:
            line2=line.replace("Y"+Y,"Y"+Y0)
            line2=line2.replace("X"+X,"X"+X0)
            sys.stdout.write(line2)
            sys.stdout.write(line)
    if len(lB) > 0:
        B=lB[0]
    if len(lF) > 0:
        F=lF[0]
    X1=X0
    Y1=Y0
    X0=X
    Y0=Y

sys.stdout.flush()
