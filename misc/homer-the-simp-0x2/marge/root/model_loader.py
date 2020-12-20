#!/usr/bin/python3
from zipfile import ZipFile
import pickle
import sys
import os

guid = 1000

os.setgroups([])
os.setgid(guid)
os.setuid(guid)

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} archive.pth")
    sys.exit(-1)

# Fixed during the CTF, thanks @MinatoTW for reporting the
# challenge was not working properly.
# It turns out that the `torch.load` function passes the
# model to pickle without even verifying that it's a valid
# ZIP archive, which is really weird. This makes it possible
# to get RCE with a single pickle file, without the need
# to craft a valid model.
# PS: The whole point from simulating how `torch.load` works
# instead of downloading PyTorch, is to avoid bloating the
# container unnecessarily for a single function.
try:
    pickle.load(open(sys.argv[1], "rb"))
    exit(0)
except:
    pass

pkl_file = "archive/data.pkl"
archive = ZipFile(sys.argv[1])

if pkl_file in archive.namelist():
    archive.extract(pkl_file, path="/tmp")
    pkl = open(f"/tmp/{pkl_file}", "rb")
    pickle.load(pkl)

