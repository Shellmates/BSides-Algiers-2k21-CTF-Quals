CC=arm-linux-gnueabihf-gcc
STRIP=arm-linux-gnueabihf-strip
CFLAGS=-fno-stack-protector -no-pie -z execstack
SOURCE=arm32.c
OUTFILE=challenge/arm32

build: $(SOURCE)
	$(CC) $(CFLAGS) -D BuiltWithMake -o $(OUTFILE) $(SOURCE)
	$(STRIP) -N _gadgets $(OUTFILE)
	chmod +x $(OUTFILE)
