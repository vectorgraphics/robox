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

#for j in range(ny):
#    y0=yoffset+j*my
#    for i in range(nx):
#        x0=xoffset+i*mx
for i in range(nx):
    x0=xoffset+i*mx
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G39"])
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 X105Y75"])
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G28 Z"])
    subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G39 S1.0"])
    z0=0
    for j in range(ny):
        y0=yoffset+j*my
        subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z2"])
        subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 X"+str(x0)+"Y"+str(y0)])
        subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G28 Z"])
        wait()
        subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","G0 Z2"])
        line=subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M113"])
        z0 += float(rdelta.findall(str(line))[0])
#        sys.stdout.write(str(x0)+" "+str(y0)+" "+str(z0)+" "+str(z)+"\n")
        sys.stdout.write(str(z0)+" ")
        sys.stdout.flush()
    sys.stdout.write("\n")
subprocess.check_output(["sudo","/u/bowman/bin/rbx","gcode","M139 S0"])
