#!/usr/bin/python3 

from PIL import Image 
from pytesseract import image_to_string as extract
import os 

for f in range(50,-1,-1):

	img = Image.open('password.png')
	pixels = img.load()
	w,l = img.size

	keys = [int(i) for i in open('shift_keys').readlines()]

	for i in range(l):
		backup = []	
		for j in range(w):
			backup += [pixels[j,i]]

		for j in range(w):
			pixels[(j - keys[i]) % w, i] = backup[j]

	file = 'UnzipME{}.zip'.format(f)
	password = extract(img).strip().upper().replace(' ','')
	os.system('unzip -o -P {} {}'.format(password,file))
	os.system('rm {}'.format(file))
os.system('rm shift_keys password.png')
print(open('flag.txt').read())
