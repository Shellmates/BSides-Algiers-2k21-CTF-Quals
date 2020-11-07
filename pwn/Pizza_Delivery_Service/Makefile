CC=gcc
CFLAGS=-fno-stack-protector
SOURCE=src/pizza-service.c
OUTFILE=challenge/pizza-service

build: $(SOURCE)
	$(CC) $(CFLAGS) -D BuiltWithMake -o $(OUTFILE) $(SOURCE)
	chmod +x $(OUTFILE)
