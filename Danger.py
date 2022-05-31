#!/bin/python3 python3
import os
import stat
import string
import subprocess
import time

drives = [];

letters = list(string.ascii_lowercase)
letters.extend([i+b for i in letters for b in letters])

for letter in letters:
  if letter != 'a':
    drives.append([letter,"/dev/sd"+letter,0,1])
#print(drives)

def isblockdevice(path):
  return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

while True:
  print("Waiting for devices")
  for x in drives:
      BlkDev = isblockdevice(x[1])
      if BlkDev == False:
        x[2] = 0
      if BlkDev == True and x[2] == 0:
        x[2] = 1
        Spinner = subprocess.getoutput('cat /sys/block/sd'++'/queue/rotational')
        x[3] = Spinner
        if Spinner == '0':
          print('Got SSD '+x[1]+", You have been granted summary distruction, thank you for your service.")
          subprocess.run(["umount", x[1]+'?*'])
          subprocess.Popen(['blkdiscard', '-z',  x[1]])
        else:
          print('Got Spinner '+x[1]+", You have been granted summary distruction, thank you for your service.")
          subprocess.run(["umount", x[1]+'?*'])
          subprocess.Popen(['shred', '-v', '-n7', '-z', x[1]])
  time.sleep(1)
