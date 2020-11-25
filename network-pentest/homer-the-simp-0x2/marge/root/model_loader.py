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

pkl_file = "archive/data.pkl"
archive = ZipFile(sys.argv[1])

if pkl_file in archive.namelist():
    archive.extract(pkl_file, path="/tmp")
    pkl = open(f"/tmp/{pkl_file}", "rb")
    pickle.load(pkl)
