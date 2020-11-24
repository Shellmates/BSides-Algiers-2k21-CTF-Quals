CC=gcc
CFLAGS=-fno-stack-protector -no-pie
SOURCE=l33t-club.c
OUTFILE=challenge/l33t-club

build: $(SOURCE)
	$(CC) $(CFLAGS) -D BuiltWithMake -o $(OUTFILE) $(SOURCE)
	chmod +x $(OUTFILE)
