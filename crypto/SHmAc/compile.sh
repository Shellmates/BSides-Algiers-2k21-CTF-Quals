gcc SHmAc.c -o SHmAc -Wl,-z,relro,-z,now -fstack-protector -lcrypto -lb64
