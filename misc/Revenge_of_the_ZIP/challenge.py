#!/usr/bin/python

import os , string , random
from PIL import Image , ImageFont , ImageDraw

chars =  string.digits

def rand_password():
	return ''.join(random.choice(chars) for _ in range(10))

def create_image(txt):
	img = Image.new('RGB',(200,60),color=(0,0,0))
	font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 30)
	d = ImageDraw.Draw(img)
	d.text((20,20),txt,font=font,fill=(34,139,34))
	scramble_img(img)

def scramble_img(img):
	pixels = img.load()
	w , l = img.size
	keys = []	

	for i in range(l):
		backup = []
		key = random.randint(0,w-1)	
		keys.append(str(key)+"\n")
		
		for j in range(w):
			backup += [pixels[j,i]]

		for j in range(w):
			pixels[(j + key) % w, i] = backup[j]
	img.save('password.png')

	with open('shift_keys','w') as f :
		for k in keys :
			f.write(k)

def main():
	password = rand_password()
	os.system('zip -P {} UnzipME0.zip flag.txt'.format(password))
	create_image(password)

	for i in range(1,51):

		ex_file = 'UnzipME{}.zip'.format(i-1)
		file = 'UnzipME{}.zip'.format(i)
		password = rand_password()
		os.system('zip -P {} {} {} {} {}'.format(password,file,ex_file,"password.png","shift_keys"))
		os.system('rm {}'.format(ex_file))
		create_image(password)


if __name__ == '__main__':
	main()