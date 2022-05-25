#!/usr/bin/env python3
import os
import stat
import subprocess

drives = [["d","/dev/sdd",0],["e","/dev/sde",0],["d","/dev/sdf",0]]

def isblockdevice(path):
  return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

for x in drives:
    BlkDev = isblockdevice(x[1])
    if BlkDev == True and x[2] == 0:
        x[2] = 1
        print("Murder that drive!! "+x[1])
        process = subprocess.run(['dd if=/dev/urandom of='+x[1]+' bs=1M', 'Even more output'], 
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
        
    else:
        x[2] = 0
        process