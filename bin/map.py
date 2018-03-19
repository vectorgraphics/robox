#!/usr/bin/env python3
import fileinput
import sys
import re
import subprocess
import time

numeric="([-+]?(?:(?: \d* \. \d+ )|(?: \d+ \.? )))"
rZ=re.compile("Z:"+numeric,re.VERBOSE)
rdelta=re.compile("delta:"+numeric,re.VERBOSE)

Length=204
Width=149

Xcenter=105
Ycenter=75

X=Length
Y=Width
    
nx=21
ny=15

if(nx%2 == 0):
    nx=nx-1
if(ny%2 == 0):
    ny=ny-1

mx=int(Xcenter/((nx-1)//2))
my=int(Ycenter/((ny-1)//2))

xoffset=Xcenter-(nx-1)//2*mx
yoffset=Ycenter-(ny-1)//2*my

z=0

def wait():
    while True:
        line=str(subprocess.check_output(["rbx","status"]))
        if re.match("b'Printer idle",line):
            break
    return

subprocess.check_output(["rbx","gcode","M139"])
subprocess.check_output(["rbx","gcode","G0 Z2"])
subprocess.check_output(["rbx","gcode","T0"])
subprocess.check_output(["rbx","gcode","M107"])
subprocess.check_output(["rbx","gcode","M190"])

for i in range(nx):
    x0=xoffset+i*mx
    if x0 > Length:
        break
    sys.stdout.write(str(x0)+" ")
sys.stdout.write("\n")
for j in range(ny):
    y0=yoffset+j*my
    if y0 > Width:
        break
    sys.stdout.write(str(y0)+" ")
sys.stdout.write("\n")
sys.stdout.flush()

def probe(x0,y0):
    subprocess.check_output(["rbx","gcode","G0 Z2"])
    subprocess.check_output(["rbx","gcode","G0 X"+str(x0)+"Y"+str(y0)])
    subprocess.check_output(["rbx","gcode","G28 Z"])
    wait()
    subprocess.check_output(["rbx","gcode","G0 Z2"])
    return subprocess.check_output(["rbx","gcode","M113"])

subprocess.check_output(["rbx","gcode","G39"])
subprocess.check_output(["rbx","gcode","G0 X"+str(Xcenter)+"Y"+str(Ycenter)])
subprocess.check_output(["rbx","gcode","G28 Z"])
subprocess.check_output(["rbx","gcode","G39 S1.0"])
subprocess.check_output(["rbx","gcode","G0 Z2"])

Z0=[0]*nx
n=4

for j in range(n):
    z0=0
    for i in range(nx):
        x0=xoffset+i*mx
        if x0 > Length:
            break
        line=probe(x0,yoffset)
        z0 += float(rdelta.findall(str(line))[0])
        Z0[i] += z0
    subprocess.check_output(["rbx","gcode",
                             "G0 X"+str(Xcenter)+"Y"+str(Ycenter)])
    subprocess.check_output(["rbx","gcode","G28 Z"])
    subprocess.check_output(["rbx","gcode","G0 Z2"])

for i in range(nx):
    Z0[i] /= n
    
for i in range(nx):
    x0=xoffset+i*mx
    if x0 > Length:
        break
    probe(x0,yoffset)
    z0=Z0[i]
    sys.stdout.write(str(z0)+" ")
    for j in range(1,ny):
        y0=yoffset+j*my
        if y0 > Width:
            break
        line=probe(x0,y0)
        z0 += float(rdelta.findall(str(line))[0])
        sys.stdout.write(str(z0)+" ")
        sys.stdout.flush()
    sys.stdout.write("\n")
subprocess.check_output(["rbx","gcode","M139 S0"])
