CC=gcc
CFLAGS=-fno-stack-protector -no-pie
SOURCE=welcome.c
OUTFILE=challenge/welcome

build: $(SOURCE)
	$(CC) $(CFLAGS) -D BuiltWithMake -o $(OUTFILE) $(SOURCE)
	chmod +x $(OUTFILE)
