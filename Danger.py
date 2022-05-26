#!/bin/python3 python3
import os
import stat
import subprocess
import time

drives = [["b","/dev/sdb",0],["c","/dev/sdc",0],["d","/dev/sdd",0],["e","/dev/sde",0],["f","/dev/sdf",0],["g","/dev/sdg",0],["h","/dev/sdh",0],["i","/dev/sdi",0],["j","/dev/sdj",0],["k","/dev/sdk",0],["l","/dev/sdl",0],["m","/dev/sdm",0]]

def isblockdevice(path):
  return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

print("Waiting for devices")
while True:
  
  for x in drives:
      BlkDev = isblockdevice(x[1])
      if BlkDev == False:
        x[2] = 0
      if BlkDev == True and x[2] == 0:
        x[2] = 1
        print('Got '+x[1]+", You have been granted summary distruction, thank you for your service.")
        subprocess.call(['sudo umount '+x[1]+'?*'])
        subprocess.Popen(['sudo shred -v -n7 -z '+x[1]])
        print("Waiting for devices")
  time.sleep(1)