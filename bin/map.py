#!/usr/bin/env python3
import fileinput
import sys
import re
import subprocess
import time

numeric="([-+]?(?:(?: \d* \. \d+ )|(?: \d+ \.? )))"
rZ=re.compile("Z:"+numeric,re.VERBOSE)
rdelta=re.compile("delta:"+numeric,re.VERBOSE)

Length=200
Width=150

ygap=11

X=Length
Y=Width-ygap
    
nx=21
ny=16

mx=int(X/(nx-1))
my=int(Y/(ny-1))

xoffset=(X-(nx-1)*mx)/2+2
yoffset=ygap+(Y-(ny-1)*my)/2

z=0

def wait():
    global z
    output=""
    time.sleep(1)
    while True:
        line=str(subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M114"]))
#        sys.stdout.write(line+"\n")
        z=float(rZ.findall(str(line))[0])
        if line == output and z <= 0.2:
            break
        time.sleep(0.5)
        output=line
    return

subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M139"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z4"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z2"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 X105Y75"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","T0"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M107"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M190"])

for i in range(nx):
    sys.stdout.write(str(xoffset+i*mx)+" ")
sys.stdout.write("\n")
for j in range(ny):
    sys.stdout.write(str(yoffset+j*my)+" ")
sys.stdout.write("\n")

def probe(x0,y0):
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z2"])
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 X"+str(x0)+"Y"+str(y0)])
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G28 Z"])
    wait()
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z2"])
    return subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M113"])

subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G39"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 X105Y75"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G28 Z"])
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G39 S1.0"])

Z0=[0]*nx
z0=0

for i in range(nx):
    x0=xoffset+i*mx
    line=probe(x0,yoffset)
    z0 += float(rdelta.findall(str(line))[0])
    Z0[i]=z0
    
for i in range(nx):
    x0=xoffset+i*mx
    probe(x0,yoffset)
    z0=Z0[i]
    sys.stdout.write(str(z0)+" ")
    for j in range(1,ny):
        y0=yoffset+j*my
        line=probe(x0,y0)
        z0 += float(rdelta.findall(str(line))[0])
        sys.stdout.write(str(z0)+" ")
        sys.stdout.flush()
    sys.stdout.write("\n")
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M139 S0"])
